#!/bin/bash
set -e

cd "$(dirname "$0")/.."
source /tmp/sky/bin/activate

# Locate CUDA_HOME so flashinfer JIT can find nvcc at runtime
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

# Clear stale flashinfer JIT cache
rm -rf ~/.cache/flashinfer

# Download data from S3
DATA_DIR="/home/ec2-user/xin/data_qwen3b_v3"
mkdir -p "$DATA_DIR"
echo "Downloading parquet data from S3..."
aws s3 cp s3://endless-terminals-training/prepared_data/train.parquet "$DATA_DIR/train.parquet"
aws s3 cp s3://endless-terminals-training/prepared_data/validation.parquet "$DATA_DIR/validation.parquet"
echo "Data ready."

# Auto-detect resume mode
CKPT_DIR="/home/ec2-user/xin/checkpoints_qwen3b_v3"
S3_CKPT="s3://endless-terminals-training/qwen2.5-3b-v3"

if [ -f "$CKPT_DIR/latest_ckpt_global_step.txt" ]; then
  RESUME_MODE=latest
  echo "Found existing checkpoint, resuming from latest."
else
  RESUME_MODE=null
  echo "No checkpoint found, starting fresh."
fi

LOG_FILE="$CKPT_DIR/train_debug.log"
mkdir -p "$CKPT_DIR"

# Background watcher: uploads each new checkpoint to S3 as soon as it's saved
(
  UPLOADED=""
  while true; do
    for step_dir in "$CKPT_DIR"/global_step_*/; do
      step=$(basename "$step_dir")
      if [ -f "$step_dir/trainer_state.pt" ] && ! echo "$UPLOADED" | grep -q "$step"; then
        echo "[uploader] Uploading $step to S3..."
        aws s3 sync "$step_dir" "$S3_CKPT/$step/" --no-progress --quiet
        echo "[uploader] $step uploaded to $S3_CKPT/$step/"
        latest=$(cat "$CKPT_DIR/latest_ckpt_global_step.txt" 2>/dev/null)
        if [ "$step" != "global_step_$latest" ]; then
          rm -rf "$step_dir"
          echo "[uploader] $step deleted from disk"
        else
          echo "[uploader] $step kept on disk (latest checkpoint)"
        fi
        UPLOADED="$UPLOADED $step"
      fi
    done
    sleep 30
  done
) &
UPLOADER_PID=$!
echo "S3 uploader started (PID $UPLOADER_PID)"

# Background log syncer: uploads training log and evals to S3 every 5 minutes
(
  while true; do
    sleep 300
    aws s3 cp "$LOG_FILE" "$S3_CKPT/train_debug.log" --quiet 2>/dev/null
    aws s3 sync "/home/ec2-user/xin/exports_qwen3b_v3/" "$S3_CKPT/evals/" --quiet 2>/dev/null
  done
) &
LOG_SYNC_PID=$!
echo "Log syncer started (PID $LOG_SYNC_PID)"

# Run training
RAY_memory_usage_threshold=0.99 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
HF_HOME=/tmp/hf_cache \
WANDB_MODE=offline \
SKYRL_DUMP_INFRA_LOG_TO_STDOUT=1 \
VLLM_ATTENTION_BACKEND=TORCH_SDPA \
python -m train.main_endless \
  "data.train_data=['$DATA_DIR/train.parquet']" \
  "data.val_data=['$DATA_DIR/validation.parquet']" \
  environment.env_class=endless \
  trainer.policy.model.path=Qwen/Qwen2.5-3B-Instruct \
  trainer.critic.model.path=Qwen/Qwen2.5-3B-Instruct \
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
  trainer.train_batch_size=4 \
  trainer.policy_mini_batch_size=4 \
  trainer.critic_mini_batch_size=4 \
  trainer.micro_forward_batch_size_per_gpu=1 \
  trainer.micro_train_batch_size_per_gpu=1 \
  trainer.max_prompt_length=4096 \
  trainer.epochs=2 \
  trainer.update_epochs_per_batch=2 \
  trainer.ckpt_interval=100 \
  trainer.eval_interval=20 \
  trainer.eval_batch_size=10 \
  trainer.max_ckpts_to_keep=1 \
  trainer.logger=console \
  "trainer.project_name=simrl-sky-endless" \
  "trainer.run_name=endless-ppo-qwen3b-v3" \
  "trainer.ckpt_path=$CKPT_DIR" \
  "trainer.export_path=/home/ec2-user/xin/exports_qwen3b_v3" \
  trainer.resume_mode=null \
  generator.inference_engine.num_engines=1 \
  generator.inference_engine.tensor_parallel_size=4 \
  generator.inference_engine.run_engines_locally=true \
  generator.inference_engine.backend=vllm \
  generator.inference_engine.weight_sync_backend=nccl \
  generator.inference_engine.async_engine=true \
  generator.inference_engine.gpu_memory_utilization=0.35 \
  generator.n_samples_per_prompt=4 \
  generator.max_turns=8 \
  "environment.skyrl_gym.max_env_workers=10" \
  "generator.sampling_params.max_generate_length=2048" \
  "generator.sampling_params.temperature=0.6" \
  2>&1 | tee "$LOG_FILE"

# Kill the uploader when training finishes
kill $UPLOADER_PID 2>/dev/null
kill $LOG_SYNC_PID 2>/dev/null

# Final sync: upload log and all evals to S3
echo "Uploading final log and evals to S3..."
aws s3 cp "$LOG_FILE" "$S3_CKPT/train_debug.log" --no-progress
aws s3 sync "/home/ec2-user/xin/exports_qwen3b_v3/" "$S3_CKPT/evals/" --no-progress
echo "Training complete. All metrics uploaded to S3."
