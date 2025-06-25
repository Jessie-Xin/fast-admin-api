#!/bin/bash

# 启动FastAPI应用
poetry run fastapi dev app/main.py --app app

# 如果需要指定端口，可以使用以下命令
# poetry run uvicorn app.main:app --reload --port 8000 