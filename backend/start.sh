#!/bin/bash
# 启动脚本
set -e  # 遇到错误退出
echo "当前目录: $(pwd)"
echo "切换到backend目录..."
cd /opt/render/project/src/backend || { echo "无法进入backend目录"; exit 1; }
echo "切换后目录: $(pwd)"
echo "目录内容:"
ls -la
echo "Python路径: $PYTHONPATH"
echo "启动uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT