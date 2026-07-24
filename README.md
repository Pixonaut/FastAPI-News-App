# FastAPI 新闻资讯后端 API

基于 FastAPI + SQLAlchemy 异步 ORM 开发的新闻资讯后端服务。

## 技术栈

- **框架**：FastAPI
- **ORM**：SQLAlchemy（异步）
- **数据库**：MySQL（aiomysql）
- **数据校验**：Pydantic V2
- **缓存**：Redis
- **密码加密**：bcrypt

## 功能模块

- **新闻**：分类列表、分页列表、新闻详情（含浏览量统计和相关推荐）
- **用户**：注册、登录、token 认证、信息修改、密码修改
- **收藏**：检查、添加、取消、分页列表、清空

## 启动

1. 确保 MySQL 运行，创建数据库 `news_app`
2. 配置 `config/db_conf.py` 中的数据库连接信息
3. 确保 Redis 运行（可选，不影响基础功能）
4. 启动后端：

```bash
cd 项目目录
.venv\Scripts\activate
uvicorn main:app --reload
```

5. 访问 `http://127.0.0.1:8000/docs` 查看接口文档

## 项目结构

```
├── main.py              # 应用入口
├── config/              # 数据库、缓存配置
├── models/              # ORM 模型
├── schemas/             # Pydantic 数据校验
├── crud/                # 数据操作层
├── routers/             # API 路由
├── cache/               # Redis 缓存
└── utils/               # 工具（认证、异常处理、响应封装）
```
