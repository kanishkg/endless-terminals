
from __future__ import annotations
import os
# os.environ.setdefault("AZURE_LOG_LEVEL", "ERROR")
import random
import time
import logging
import sys
from pathlib import Path
import shutil
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import textwrap

from tqdm import tqdm

from openai import AzureOpenAI, OpenAI, AsyncOpenAI


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)


MAX_RETRIES = 5


# Cache the client to avoid recreating it
@lru_cache(maxsize=None)
def get_client() -> AzureOpenAI:
    """Get or create a cached vllm OpenAI client."""

    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="nokey"
    )
    return client

def chat_completion_batch(
    messages: List[List[Dict[str, str]]],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    num_completions: int = 1,
    max_concurrency: int = 64,
    show_progress: bool = True,
) -> List[Any]:
    """Submit multiple chat completion requests concurrently with improved performance."""
    

    # vllm client
    client = OpenAI(base_url="http://localhost:8000/v1", api_key="nokey")
    clients = {
        model : client
    }
    model_keys = list(clients.keys())
    max_retries = MAX_RETRIES
    
    def _one_with_retry(idx: int, msgs: List[Dict[str, str]]):
        """Execute a single request with retry logic."""
        last_error = None

        for attempt in range(max_retries):
            try:
                model = model_keys[(idx + attempt) % len(model_keys)]
                client = clients[model]

                resp = client.chat.completions.create(
                    model=model,
                    messages=msgs,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=num_completions,
                    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                )
                return resp
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Determine if we should retry
                if attempt < max_retries - 1:
                    # Calculate backoff time
                    if "rate" in error_str.lower():
                        wait_time = min(2 ** (attempt + 2), 30)  # Rate limit backoff
                    elif "timeout" in error_str.lower():
                        wait_time = 2  # Short wait for timeout
                    else:
                        wait_time = 2 ** attempt  # General exponential backoff
                    
                    time.sleep(wait_time)
                else:
                    raise last_error
    
    results: List[Any] = [None] * len(messages)
    
    # Process requests concurrently
    with ThreadPoolExecutor(max_workers=max_concurrency) as pool:
        # Submit all tasks
        future_to_idx = {
            pool.submit(_one_with_retry, i, m): i 
            for i, m in enumerate(messages)
        }
        
        # Process completed futures with a reliable progress bar
        pbar = tqdm(
            total=len(messages),
            disable=False,
            dynamic_ncols=True,
            desc="Processing",
            unit="req",
            miniters=1,
            file=sys.stdout,
        )
        try:
            for fut in as_completed(future_to_idx):
                idx = future_to_idx[fut]
                try:
                    results[idx] = fut.result()
                except Exception as e:
                    # logger.error(f"Failed to process request {idx + 1}: {str(e)}")
                    results[idx] = None  # Mark as failed
                finally:
                    pbar.update(1)
        finally:
            pbar.close()
    
    failed_indices = [i for i, r in enumerate(results) if r is None]
    if failed_indices:
        logger.warning(f"Failed requests: {failed_indices}")
    
    return results


def parse_python_code(code: str) -> str:
    """Extract the raw Python code from an LLM response string.

    The language-model may wrap the code in Markdown triple-backtick fences
    (optionally annotated with a language tag like ``python``) or include
    additional explanatory text.  This helper returns **only** the actual
    Python source, trimmed and left-dedented so it can be written directly
    to a ``.py`` file.
    """
    import re
    # First, look for a fenced code block – we assume the first one contains
    # the pytest file we are interested in.
    fence_regex = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL | re.IGNORECASE)
    match = fence_regex.search(code)
    if match:
        snippet = match.group(1)
    else:
        # Fallback – treat the whole string as code.
        snippet = code
    # Normalise indentation & strip trailing whitespace/newlines
    return textwrap.dedent(snippet).rstrip()  # type: ignore[arg-type]

def check_python_code(code: str) -> bool:
    """Check if the Python code compiles successfully."""
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False
    except Exception as e:
        return False

