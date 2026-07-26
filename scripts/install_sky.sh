#!/bin/bash
set -e

# Must be run from the project root (directory containing this script's parent)
cd "$(dirname "$0")/.."

if [ ! -d "SkyRL" ]; then
  git clone https://github.com/novasky-ai/SkyRL.git
fi

python3.13 -m venv /tmp/sky
source /tmp/sky/bin/activate

# Locate CUDA_HOME: try standard locations first, then find nvcc via PATH
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

pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install packaging wheel setuptools_scm "setuptools<75"

# Apply patches to SkyRL (idempotent — safe to re-run)
python3.13 scripts/_apply_patches.py

PIP_NO_BUILD_ISOLATION=1 pip install -e "SkyRL[fsdp]"
pip install "ray[default]==2.51.1"
pip install -e .

# Symlink nvcc into the venv's nvidia package so flashinfer JIT finds it
VENV_NVCC_DIR="/tmp/sky/lib64/python3.13/site-packages/nvidia/cu13/bin"
if [ ! -f "$VENV_NVCC_DIR/nvcc" ]; then
  mkdir -p "$VENV_NVCC_DIR"
  ln -sf "$CUDA_HOME/bin/nvcc" "$VENV_NVCC_DIR/nvcc"
  echo "Symlinked nvcc into venv at $VENV_NVCC_DIR/nvcc"
fi

# Symlink lib64 -> lib in CUDA_HOME so the linker finds libcudart
if [ ! -e "$CUDA_HOME/lib64" ]; then
  ln -sf "$CUDA_HOME/lib" "$CUDA_HOME/lib64"
  echo "Symlinked $CUDA_HOME/lib64 -> lib"
fi

# Fix prometheus_fastapi_instrumentator routing bug
PROM_FILE="/tmp/sky/lib64/python3.13/site-packages/prometheus_fastapi_instrumentator/routing.py"
if [ -f "$PROM_FILE" ]; then
  sed -i 's/route_name = route.path/route_name = getattr(route, "path", None)/' "$PROM_FILE"
fi

echo "Done. Activate with: source /tmp/sky/bin/activate"
