# Family Chef

家常主厨采用轻量 Monorepo 管理。用户端、管理端和后端位于同一个 Git
仓库中，但各自保留独立依赖和锁文件，不引入额外的 workspace 或任务编排框架。

## 目录

```text
family-chef/
├── front/          # uni-app 用户端，支持 H5 和微信小程序
├── admin/          # Vue 3 Web 管理端
├── server/         # Django REST Framework API
├── docs/           # 架构和实施文档
├── HowToCook/      # 本地菜谱导入源，不纳入 Git
└── CookLikeHOC/    # 本地菜谱导入源，不纳入 Git
```

`HowToCook/` 和 `CookLikeHOC/` 只作为本地数据源使用，已在根 `.gitignore`
中排除。执行菜谱导入前，需要自行准备这两个目录，或通过环境变量
`HOWTOCOOK_PATH`、`COOKLIKEHOC_PATH` 指向对应数据源。

## 菜谱来源

本项目菜谱内容借鉴并整理自以下 GitHub 开源项目：

- HowToCook: https://github.com/Anduin2017/HowToCook
- CookLikeHOC: https://github.com/Gar-b-age/CookLikeHOC

导入脚本会从上述项目的本地副本中解析菜名、分类、材料、步骤和来源链接，并重新整理为适合用户端、管理端和后端 API 使用的数据结构。

## 环境要求

- Node.js 20 或兼容版本
- npm
- Python 3.12
- uv

## 常用命令

```bash
make install
make migrate
make export-recipes-json
cd server && uv run python manage.py import_recipes --file data/recipes.json --publish
make dev-server
make dev-admin
make dev-h5
```

更多命令执行 `make help` 查看。各子项目的具体说明参见
`admin/README.md`、`server/README.md` 和 `docs/backend-admin-plan.md`。

## 本地访问地址

启动对应服务后，可通过以下地址访问：

| 端 | 地址 | 启动命令 |
| --- | --- | --- |
| 用户端 H5 | http://127.0.0.1:5173/ | `make dev-h5` |
| 管理端 | http://127.0.0.1:5174/ | `make dev-admin` |
| 后端 API | http://127.0.0.1:8000/api/v1/ | `make dev-server` |
| API 文档 | http://127.0.0.1:8000/api/docs/ | `make dev-server` |
| Django Admin | http://127.0.0.1:8000/django-admin/ | `make dev-server` |

H5 开发服务如果检测到端口占用，Vite 会自动切换端口，请以终端输出为准。

微信小程序没有浏览器访问地址，执行 `make build-weixin` 后，使用微信开发者工具导入：

```text
front/dist/build/mp-weixin/
```

## 依赖策略

- `front/package-lock.json` 和 `admin/package-lock.json` 分别锁定 Node 依赖。
- `server/uv.lock` 锁定 Python 依赖。
- 不提交 `node_modules`、构建产物、虚拟环境、本地数据库或 `.env`。
- 跨端共享代码达到实际规模后，再评估 pnpm workspace 或任务缓存工具。
