import re, pathlib

# --- pyproject.toml: remove incompatible deps, bump vllm ---
f = pathlib.Path('SkyRL/pyproject.toml')
txt = f.read_text()
changed = False

replacements = [
    ('vllm==0.20.2', 'vllm==0.21.0'),
]
removals = [
    'flashinfer-jit-cache',
    'causal-conv1d',
    'flash-attn',
]

for old, new in replacements:
    if old in txt:
        txt = txt.replace(old, new)
        changed = True

for pattern in removals:
    new_txt = re.sub(rf'^\s*"[^"]*{re.escape(pattern)}[^"]*"[^\n]*\n', '', txt, flags=re.MULTILINE)
    if new_txt != txt:
        txt = new_txt
        changed = True

# Remove standalone key entries (non-quoted lines) for these patterns
for pattern in removals:
    new_txt = re.sub(rf'^{re.escape(pattern)}\s*=.*\n', '', txt, flags=re.MULTILINE)
    if new_txt != txt:
        txt = new_txt
        changed = True

if changed:
    f.write_text(txt)
    print('Patched pyproject.toml')
else:
    print('pyproject.toml already patched, skipping')

# --- model_wrapper.py: make flash_attn import optional ---
f = pathlib.Path('SkyRL/skyrl/backends/skyrl_train/workers/model_wrapper.py')
txt = f.read_text()
old = 'from flash_attn.bert_padding import pad_input, unpad_input'
new = 'try:\n    from flash_attn.bert_padding import pad_input, unpad_input\nexcept ImportError:\n    pad_input = None\n    unpad_input = None'
if new in txt:
    print('model_wrapper.py already patched, skipping')
elif old in txt:
    f.write_text(txt.replace(old, new))
    print('Patched model_wrapper.py')
else:
    print('model_wrapper.py: flash_attn import not found, skipping')

# --- ppo_utils.py: replace decorator-based registration with explicit calls ---
f = pathlib.Path('SkyRL/skyrl/backends/skyrl_train/utils/ppo_utils.py')
txt = f.read_text()
old = '@register_policy_loss(PolicyLossType.REGULAR)\n@register_policy_loss(PolicyLossType.DUAL_CLIP)\ndef ppo_policy_loss('
new_def = 'def ppo_policy_loss('
already_patched = (
    'PolicyLossRegistry.register(PolicyLossType.REGULAR, ppo_policy_loss)' in txt
    and new_def in txt
    and old not in txt
)
if already_patched:
    print('ppo_utils.py already patched, skipping')
elif old in txt:
    txt = txt.replace(old, new_def)
    txt = re.sub(
        r'(def ppo_policy_loss\(.*?return loss, loss_metrics\n)',
        r'\1\nPolicyLossRegistry.register(PolicyLossType.REGULAR, ppo_policy_loss)\nPolicyLossRegistry.register(PolicyLossType.DUAL_CLIP, ppo_policy_loss)\n',
        txt, count=1, flags=re.DOTALL
    )
    f.write_text(txt)
    print('Patched ppo_utils.py')
else:
    print('ppo_utils.py: decorator pattern not found, skipping')

# --- new_inference_worker_wrap.py: remove LayerwiseReloadWorkerMixin inheritance
#     (vLLM 0.21.0 provides start/finish_weight_update natively) ---
f = pathlib.Path('SkyRL/skyrl/backends/skyrl_train/inference_servers/new_inference_worker_wrap.py')
txt = f.read_text()
already_patched = (
    'LayerwiseReloadWorkerMixin' not in txt
    and '_weight_update_active' in txt
)
if already_patched:
    print('new_inference_worker_wrap.py already patched, skipping')
else:
    txt = re.sub(
        r'from skyrl\.backends\.skyrl_train\.inference_servers\.layerwise_reload import \(\s*LayerwiseReloadWorkerMixin,?\s*\)\n+',
        '',
        txt
    )
    txt = txt.replace(
        'class NewInferenceWorkerWrap(LayerwiseReloadWorkerMixin):',
        'class NewInferenceWorkerWrap:'
    )
    txt = txt.replace('_skyrl_weight_update_active', '_weight_update_active')
    txt = txt.replace('_skyrl_is_checkpoint_format', '_is_checkpoint_format')
    f.write_text(txt)
    print('Patched new_inference_worker_wrap.py')

# --- generators/base.py: add std_reward field to MetricsOutput ---
f = pathlib.Path('SkyRL/skyrl/train/generators/base.py')
txt = f.read_text()
old = 'class MetricsOutput(TypedDict):\n    avg_score: Optional[float]\n    pass_at_n: Optional[float]\n    mean_positive_reward: Optional[float]'
new = 'class MetricsOutput(TypedDict):\n    avg_score: Optional[float]\n    pass_at_n: Optional[float]\n    mean_positive_reward: Optional[float]\n    std_reward: Optional[float]'
if 'std_reward' in txt:
    print('generators/base.py already patched, skipping')
elif old in txt:
    f.write_text(txt.replace(old, new))
    print('Patched generators/base.py')
else:
    print('generators/base.py: MetricsOutput pattern not found, skipping')

# --- generators/utils.py: compute and return std_reward ---
f = pathlib.Path('SkyRL/skyrl/train/generators/utils.py')
txt = f.read_text()
if 'std_reward' in txt:
    print('generators/utils.py already patched, skipping')
else:
    # Add std_reward computation for both token-level and scalar reward paths
    old_token = '        mean_raw_reward = float(np.mean([sum(trajectory_rewards) for trajectory_rewards in rewards]))'
    new_token = '        reward_sums = [sum(trajectory_rewards) for trajectory_rewards in rewards]\n        mean_raw_reward = float(np.mean(reward_sums))\n        std_raw_reward = float(np.std(reward_sums))'
    old_scalar = '        mean_raw_reward = float(np.mean(rewards))\n        mean_positive_reward = float(np.mean(np.maximum(rewards, 0.0)))'
    new_scalar = '        mean_raw_reward = float(np.mean(rewards))\n        std_raw_reward = float(np.std(rewards))\n        mean_positive_reward = float(np.mean(np.maximum(rewards, 0.0)))'
    old_return = '    return MetricsOutput(\n        avg_score=mean_raw_reward,\n        pass_at_n=pass_at_n,\n        mean_positive_reward=mean_positive_reward,\n    )'
    new_return = '    return MetricsOutput(\n        avg_score=mean_raw_reward,\n        pass_at_n=pass_at_n,\n        mean_positive_reward=mean_positive_reward,\n        std_reward=std_raw_reward,\n    )'
    changed = False
    if old_token in txt:
        txt = txt.replace(old_token, new_token)
        changed = True
    if old_scalar in txt:
        txt = txt.replace(old_scalar, new_scalar)
        changed = True
    if old_return in txt:
        txt = txt.replace(old_return, new_return)
        changed = True
    if changed:
        f.write_text(txt)
        print('Patched generators/utils.py')
    else:
        print('generators/utils.py: reward pattern not found, skipping')

# --- trainer.py: log std_reward alongside other reward metrics ---
f = pathlib.Path('SkyRL/skyrl/train/trainer.py')
txt = f.read_text()
old_reward = '            "reward/avg_raw_reward": overall_metrics["avg_score"],\n            "reward/mean_positive_reward": overall_metrics["mean_positive_reward"],\n        }'
new_reward = '            "reward/avg_raw_reward": overall_metrics["avg_score"],\n            "reward/std_reward": overall_metrics.get("std_reward", 0.0),\n            "reward/mean_positive_reward": overall_metrics["mean_positive_reward"],\n        }'
if 'reward/std_reward' in txt:
    print('trainer.py reward metrics already patched, skipping')
elif old_reward in txt:
    f.write_text(txt.replace(old_reward, new_reward))
    print('Patched trainer.py reward metrics')
else:
    print('trainer.py: reward_metrics pattern not found, skipping')

# --- worker.py: add explained_variance to critic update status ---
f = pathlib.Path('SkyRL/skyrl/backends/skyrl_train/workers/worker.py')
txt = f.read_text()
old_status = '        status = {\n            "critic_loss": loss.item(),\n            "values_mean": masked_mean(values, loss_mask).item(),\n            "values_clipfrac": clipfrac,\n            "critic_lr": self.scheduler.get_last_lr()[0],\n        }'
new_status = '        # explained_variance = 1 - var(returns - values) / var(returns)\n        with torch.no_grad():\n            returns_masked = returns[:, -num_actions:][loss_mask.bool()]\n            values_masked = values[:, -num_actions:][loss_mask.bool()]\n            var_returns = returns_masked.var().item()\n            explained_var = 1.0 - (returns_masked - values_masked).var().item() / (var_returns + 1e-8)\n        status = {\n            "critic_loss": loss.item(),\n            "values_mean": masked_mean(values, loss_mask).item(),\n            "values_clipfrac": clipfrac,\n            "explained_variance": explained_var,\n            "critic_lr": self.scheduler.get_last_lr()[0],\n        }'
if 'explained_variance' in txt:
    print('worker.py explained_variance already patched, skipping')
elif old_status in txt:
    f.write_text(txt.replace(old_status, new_status))
    print('Patched worker.py explained_variance')
else:
    print('worker.py: critic status pattern not found, skipping')
