#!/usr/bin/env bash
set -e

# =============================================
#  PythonWeb - Server Startup (Linux/macOS)
# =============================================

# --- conda 环境配置 ---
# 如果你的 conda 未初始化，取消下面这行注释并修改为你的 conda 安装路径:
# source "$HOME/miniconda3/etc/profile.d/conda.sh"

# 激活 conda 环境 (修改 py312 为你的环境名)
conda activate py312 2>/dev/null || {
    echo "[WARN] conda activate failed, using current python environment"
}

# --- 环境变量 ---
export PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd)"
export NO_COLOR=1

echo "============================================"
echo " PythonWeb - Server Startup"
echo " Python: $(which python)"
echo "============================================"

# [1/3] 数据库迁移
echo "[1/3] Running database migrations..."
python -m alembic upgrade head

# [2/3] 初始数据
echo "[2/3] Creating initial data..."
python -m app.initial_data

# [3/3] 启动服务
echo "[3/3] Starting FastAPI server..."
echo "============================================"
echo " API Docs: http://localhost:8000/docs"
echo " Health:   http://localhost:8000/api/v1/utils/health-check/"
echo "============================================"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
