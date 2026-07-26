#!/bin/bash
set -e

cd "$(dirname "$0")/.."
source /tmp/sky/bin/activate

# Locate CUDA_HOME so flashinfer JIT can find nvcc at runtime
# Try standard locations first, then find nvcc via PATH
if [ -d "/usr/local/cuda" ] && [ -f "/usr/local/cuda/bin/nvcc" ]; then
  export CUDA_HOME=/usr/local/cuda
elif [ -f "/opt/pytorch/lib/python3.13/site-packages/nvidia/cu13/bin/nvcc" ]; then
  export CUDA_HOME=/opt/pytorch/lib/python3.13/site-packages/nvidia/cu13
else
  NVCC_PATH=$(which nvcc 2>/dev/null || true)
  if [ -n "$NVCC_PATH" ]; then
    export CUDA_HOME=$(dirname $(dirname "$NVCC_PATH"))
  else
    echo "ERROR: Could not find nvcc. Set CUDA_HOME manually and re-run." >&2
    exit 1
  fi
fi
export PATH="$CUDA_HOME/bin:$PATH"
echo "Using CUDA_HOME=$CUDA_HOME"

# Clear stale flashinfer JIT cache — it embeds the nvcc path at write time
# and will fail if run was previously aborted with a wrong CUDA_HOME
rm -rf ~/.cache/flashinfer

# Auto-detect resume mode: resume from latest checkpoint if one exists
CKPT_DIR="/home/ec2-user/xin/checkpoints"
if [ -f "$CKPT_DIR/latest_ckpt_global_step.txt" ]; then
  RESUME_MODE=latest
  echo "Found existing checkpoint, resuming from latest."
else
  RESUME_MODE=null
  echo "No checkpoint found, starting fresh."
fi

LOG_FILE="$CKPT_DIR/train_debug.log"
mkdir -p "$CKPT_DIR"

RAY_memory_usage_threshold=0.99 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
HF_HOME=/tmp/hf_cache \
WANDB_MODE=offline \
SKYRL_DUMP_INFRA_LOG_TO_STDOUT=1 \
VLLM_ATTENTION_BACKEND=TORCH_SDPA \
python -m train.main_endless \
  "data.train_data=['data/train.parquet']" \
  "data.val_data=['data/validation.parquet']" \
  environment.env_class=endless \
  trainer.policy.model.path=Qwen/Qwen2.5-1.5B-Instruct \
  trainer.critic.model.path=Qwen/Qwen2.5-1.5B-Instruct \
  trainer.strategy=fsdp2 \
  trainer.algorithm.advantage_estimator=gae \
  trainer.placement.colocate_all=true \
  trainer.placement.policy_num_gpus_per_node=4 \
  trainer.placement.critic_num_gpus_per_node=4 \
  trainer.placement.ref_num_gpus_per_node=4 \
  trainer.flash_attn=false \
  trainer.remove_microbatch_padding=false \
  trainer.policy.use_torch_compile=false \
  trainer.gradient_checkpointing=true \
  trainer.train_batch_size=8 \
  trainer.policy_mini_batch_size=8 \
  trainer.critic_mini_batch_size=8 \
  trainer.micro_forward_batch_size_per_gpu=1 \
  trainer.micro_train_batch_size_per_gpu=1 \
  trainer.max_prompt_length=4096 \
  trainer.epochs=10 \
  trainer.update_epochs_per_batch=2 \
  trainer.ckpt_interval=10 \
  trainer.logger=console \
  "trainer.project_name=simrl-sky-endless" \
  "trainer.run_name=endless-ppo-qwen1.5b" \
  "trainer.ckpt_path=$CKPT_DIR" \
  "trainer.export_path=/home/ec2-user/xin/exports" \
  trainer.resume_mode=$RESUME_MODE \
  generator.inference_engine.num_engines=1 \
  generator.inference_engine.tensor_parallel_size=4 \
  generator.inference_engine.run_engines_locally=true \
  generator.inference_engine.backend=vllm \
  generator.inference_engine.weight_sync_backend=nccl \
  generator.inference_engine.async_engine=true \
  generator.inference_engine.gpu_memory_utilization=0.4 \
  generator.n_samples_per_prompt=16 \
  generator.max_turns=16 \
  "generator.sampling_params.max_generate_length=2048" \
  "generator.sampling_params.temperature=0.6" \
  2>&1 | tee "$LOG_FILE"
