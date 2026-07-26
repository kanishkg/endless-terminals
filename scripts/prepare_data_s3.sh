#!/bin/bash
set -e

# Streamline script: for each batch, download tasks + claude4.6 solutions, prepare parquet, upload, clean up
# Run from project root: bash scripts/prepare_data_s3.sh

cd "$(dirname "$0")/.."
source /tmp/sky/bin/activate

S3_BUCKET="s3://endless-terminals-training"
S3_DATA="$S3_BUCKET/data"
S3_PREPARED="$S3_BUCKET/prepared_data"
WORK_DIR="/tmp/data_work"
TASKS_BASE="/home/ec2-user/xin/harbor_tasks"  # permanent — needed at training time
OUTPUT_DIR="$WORK_DIR/parquet"

mkdir -p "$OUTPUT_DIR" "$TASKS_BASE"

BATCHES="part2_2-1 part2_2-2 part2_2-3 part2_2-4"

for BATCH in $BATCHES; do
  echo ""
  echo "=========================================="
  echo "Processing batch: $BATCH"
  echo "=========================================="

  TASKS_DIR="$TASKS_BASE/tasks_$BATCH"
  JOBS_DIR="$WORK_DIR/jobs_$BATCH"

  mkdir -p "$TASKS_DIR" "$JOBS_DIR"

  # Step 1: Download tasks
  echo "[1/4] Downloading tasks..."
  aws s3 sync "$S3_DATA/harbor_tasks_claude4.5_opus/harbor_tasks_$BATCH/" "$TASKS_DIR/" --no-progress

  # Step 2: Download solutions (4.6 sonnet only)
  echo "[2/4] Downloading solutions..."
  aws s3 sync "$S3_DATA/harbor_solutions_claude4.6_sonnet/harbor_tasks_$BATCH/" "$JOBS_DIR/" --no-progress
  # collect_harbor_results.py needs a config.json at the job dir root to treat it as a single job
  echo '{}' > "$JOBS_DIR/config.json"

  # Step 3: Merge solutions into tasks using collect_harbor_results.py
  echo "[3/4] Merging solutions into tasks..."
  python3.13 collect_harbor_results.py --jobs-dir "$JOBS_DIR" --tasks-dir "$TASKS_DIR"

  # Step 4: Generate parquet (append to existing)
  echo "[4/4] Preparing parquet..."
  python3.13 train/prepare_endless.py \
    --task-dir "$TASKS_DIR" \
    --output-dir "$OUTPUT_DIR/$BATCH"

  echo "Batch $BATCH done. Train: $(python3.13 -c "import pandas as pd; df=pd.read_parquet('$OUTPUT_DIR/$BATCH/train.parquet'); print(len(df))") rows"

  # Clean up only the jobs dir — keep tasks dir for training time
  rm -rf "$JOBS_DIR"
  echo "Cleaned up jobs for $BATCH (tasks kept at $TASKS_DIR)"
done

# Merge all batch parquets into one train + validation
echo ""
echo "=========================================="
echo "Merging all batches into final parquet..."
echo "=========================================="
python3.13 - << 'PYEOF'
import pandas as pd
import os
from pathlib import Path

output_dir = "/tmp/data_work/parquet"
final_dir = "/tmp/data_work/final"
os.makedirs(final_dir, exist_ok=True)

train_dfs, val_dfs = [], []
for batch_dir in sorted(Path(output_dir).iterdir()):
    train_f = batch_dir / "train.parquet"
    val_f = batch_dir / "validation.parquet"
    if train_f.exists():
        train_dfs.append(pd.read_parquet(train_f))
    if val_f.exists():
        val_dfs.append(pd.read_parquet(val_f))

train = pd.concat(train_dfs, ignore_index=True)
val = pd.concat(val_dfs, ignore_index=True)
train.to_parquet(f"{final_dir}/train.parquet", index=False)
val.to_parquet(f"{final_dir}/validation.parquet", index=False)
print(f"Final train: {len(train)} rows, val: {len(val)} rows")
PYEOF

# Upload final parquet to S3
echo "Uploading parquet to S3..."
aws s3 sync /tmp/data_work/final/ "$S3_PREPARED/" --no-progress

echo ""
echo "Done! Parquet available at $S3_PREPARED/"
echo "  train.parquet"
echo "  validation.parquet"
