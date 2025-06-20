# 博客后台管理系统API

使用FastAPI、SQLModel、SQLite、Poetry和OAuth2实现的博客后台管理系统API。

## 技术栈

- Python 3.12
- FastAPI：高性能Web框架
- SQLModel：结合SQLAlchemy和Pydantic的ORM库
- SQLite：轻量级数据库
- Poetry：Python依赖管理
- OAuth2：使用JWT Token的身份验证
- Alembic：数据库迁移工具

## 项目结构

```
app/
  ├── core/              # 核心配置和工具
  │   ├── config.py      # 应用配置
  │   ├── database.py    # 数据库连接
  │   ├── dependencies.py # 依赖项（认证等）
  │   └── security.py    # 安全工具（JWT、密码哈希）
  ├── models/            # 数据库模型
  │   ├── user.py        # 用户模型
  │   ├── post.py        # 文章模型
  │   ├── category.py    # 分类模型
  │   ├── tag.py         # 标签模型
  │   └── comment.py     # 评论模型
  ├── schemas/           # Pydantic验证模型
  │   ├── user.py        # 用户请求/响应模型
  │   ├── auth.py        # 认证请求/响应模型
  │   ├── post.py        # 文章请求/响应模型
  │   ├── category.py    # 分类请求/响应模型
  │   ├── tag.py         # 标签请求/响应模型
  │   ├── comment.py     # 评论请求/响应模型
  │   └── dashboard.py   # 仪表盘响应模型
  ├── routers/           # API路由
  │   ├── auth.py        # 认证路由
  │   ├── user.py        # 用户路由
  │   ├── post.py        # 文章路由
  │   ├── category.py    # 分类路由
  │   ├── tag.py         # 标签路由
  │   ├── comment.py     # 评论路由
  │   └── dashboard.py   # 仪表盘路由
  └── main.py            # 应用入口
alembic/                 # 数据库迁移配置
.env                     # 环境变量
main.py                  # 项目启动文件
```

## 安装和启动

### 选项1：使用Poetry（推荐）

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖（自动创建虚拟环境）
poetry install

# 激活虚拟环境
poetry shell
```

### 选项2：使用传统虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境（MacOS/Linux）
source venv/bin/activate
# 激活虚拟环境（Windows）
# venv\Scripts\activate

# 安装依赖
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
```

### 初始化数据库

```bash
# 使用Alembic初始化数据库
poetry run alembic upgrade head
```

### 启动服务

```bash
# 开发环境启动
poetry run python main.py

# 或使用Uvicorn直接启动
poetry run uvicorn app.main:app --reload
```

## API文档

启动服务后，可以访问以下地址查看API文档：

- Swagger文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

## 数据库迁移

```bash
# 生成迁移脚本
poetry run alembic revision --autogenerate -m "描述迁移内容"

# 应用迁移
poetry run alembic upgrade head

# 回滚一个版本
poetry run alembic downgrade -1
``` 
 