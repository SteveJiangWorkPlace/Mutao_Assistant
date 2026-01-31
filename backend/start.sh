#!/bin/bash
# 启动脚本
cd /opt/render/project/src/backend || exit 1
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $PORT