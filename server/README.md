# 家常主厨后端

基于 Python 3.12、Django 5.2 和 Django REST Framework 的模块化单体 API。
本地默认使用 SQLite，生产环境通过 `DATABASE_URL` 切换 PostgreSQL。

## 本地启动

```bash
uv sync
uv run python manage.py migrate
node ../front/scripts/export-recipes-json.mjs
uv run python manage.py import_recipes --file data/recipes.json --publish
uv run python manage.py createsuperuser
uv run python manage.py runserver 127.0.0.1:8000
```

服务启动后可访问：

- 健康检查：`http://127.0.0.1:8000/api/v1/health/`
- OpenAPI 文档：`http://127.0.0.1:8000/api/docs/`
- Django Admin：`http://127.0.0.1:8000/django-admin/`

用户端账号接口：

- 注册：`POST /api/v1/auth/register/`
- 登录：`POST /api/v1/auth/login/password/`
- 刷新令牌：`POST /api/v1/auth/token/refresh/`
- 当前用户：`GET/PATCH /api/v1/users/me/`

用户互动接口：

- 评论列表/发表：`GET/POST /api/v1/comments/`
- 评论赞踩：`POST /api/v1/comments/:id/reaction/`
- 菜品赞踩状态/操作：`GET/POST /api/v1/dishes/:id/reaction/`
- 内容举报：`POST /api/v1/reports/`

## 质量检查

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check
uv run pytest
uv run ruff check .
```

环境变量参考 `.env.example`。生产部署必须更换 `DJANGO_SECRET_KEY`、关闭
`DJANGO_DEBUG`，并配置 PostgreSQL、Redis、允许域名和 CORS 来源。
