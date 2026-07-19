# 用户端接入后端服务方案

> 版本：v1.0
> 日期：2026-07-19
> 状态：已确认，阶段 A 至阶段 C 已完成首版实施

> 实施记录：已增加规范化菜谱 JSON、幂等导入命令、公开菜品/教程 API 合同，以及 `front/` 的
> H5/微信小程序请求层、数据适配、搜索、分类、详情和静态降级。
>
> 后续进度：账号密码身份闭环，以及评论、菜品/评论赞踩和举报已接入用户端；微信和短信功能暂缓。

## 1. 目标与范围

本阶段只把现有 `front/` 用户端的“菜品浏览、分类筛选、关键词检索、菜品详情”接入
`server/` 后端。登录、微信授权、手机号、短信、评论、点赞/踩和举报保留到后续阶段。

接入完成后，H5 和微信小程序都通过统一 API 获取菜品数据，页面仍保持现有的使用方式：

- 首页展示菜品列表、分类和搜索结果。
- 详情页展示材料、步骤、技巧、耗时、难度和份量。
- 后端发布或下架菜品后，用户端不需要重新打包即可改变线上数据。
- 后端不可用时保留静态菜谱降级能力，避免当前用户端直接失效。

## 2. 当前现状

### 2.1 用户端

当前 `front/` 只有两个页面：

- `pages/index/index.vue`：直接导入 `utils/cookbook.js`，在内存中完成搜索和分类筛选。
- `pages/recipe/detail.vue`：通过本地菜谱 ID 从 `cookbook.js` 查找详情。

当前没有网络请求封装、API 基地址配置、请求错误状态、缓存策略和登录态管理。

### 2.2 后端

后端已有以下公开接口基础：

| 接口 | 当前能力 | 接入前需要确认 |
| --- | --- | --- |
| `GET /api/v1/categories/` | 返回启用的分类 | 导入分类数据并约定排序 |
| `GET /api/v1/tags/` | 返回启用的标签 | 导入标签数据并约定展示标签 |
| `GET /api/v1/dishes/` | 返回已发布菜品，支持搜索、分类、标签和排序 | 增加教程关联信息，确认分页协议 |
| `GET /api/v1/dishes/:id/` | 返回单个已发布菜品 | 建议补充当前教程摘要或 recipe ID |
| `GET /api/v1/recipes/:id/` | 返回已发布教程及当前版本 | 补齐菜品展示字段，方便详情页直接渲染 |

当前 API 默认只返回已发布数据，而本地 SQLite 尚未导入 703 道菜谱。因此必须先完成数据导入，
再切换用户端数据源。

## 3. 推荐架构

采用“API 优先 + 静态数据降级”的渐进式接入：

```text
首页 / 详情页
       |
       v
front/services/recipe-api.js       # uni.request 封装
       |
       v
front/services/recipe-adapter.js   # API 数据 -> 当前页面模型
       |
       +--> server API              # 首选数据源
       |
       +--> cookbook.js             # 网络失败时的静态降级
```

不建议在页面组件中直接调用 `uni.request`，也不建议让页面同时理解数据库字段和旧静态字段。
这样可以控制后端字段变化对 H5、小程序和页面模板的影响。

## 4. 数据导入方案

### 4.1 保留静态数据作为规范化导入源

由于根目录已经忽略 `HowToCook/` 和 `CookLikeHOC/`，新克隆项目不能依赖这两个目录完成数据库初始化。
建议将现有 `front/src/utils/cookbook.js` 的规范化结果导出为：

```text
server/data/recipes.json
```

该文件只保存已经清洗后的业务数据，不保存上游仓库的完整源码。它应当纳入 Git，作为部署和导入的
可重复输入；原始上游目录仍只作为本地重新生成数据时的可选输入。

### 4.2 导入字段映射

| 静态字段 | 数据库字段 | 说明 |
| --- | --- | --- |
| `id` | `Dish.legacy_id` | 保留旧 ID，便于兼容已有页面链接 |
| `title` | `Dish.name`、`RecipeArticle.title` | 菜品名称和教程标题 |
| `category`、`categoryLabel` | `DishCategory.key/name` | 不导入 `all`，分类按 key 去重 |
| `tags`、`method` | `Tag`、`DishTag` | 标签去重后建立关联 |
| `image` | `Dish.cover_url` | 本地静态路径或后续对象存储 URL |
| `source/sourcePath/sourceUrl` | `Dish.source_*` | 保留来源追溯信息 |
| `summary/time/difficulty/servings/tips` | `RecipeVersion` | 教程版本基础字段 |
| `ingredients` | `RecipeIngredient` | 保留 `raw_text`，结构化字段可逐步优化 |
| `steps` | `RecipeStep` | 当前步骤文本先完整保留 |

导入命令建议设计为：

```bash
cd server
uv run python manage.py import_recipes --file data/recipes.json --publish
```

命令必须支持重复执行、按 `legacy_id` 更新、生成导入报告，并在单条数据异常时记录错误而不是静默丢弃。
正式环境应先导入草稿，抽样校验后再发布；本地联调可以使用 `--publish`。

## 5. API 合同调整建议

### 5.1 菜品列表

```http
GET /api/v1/dishes/?search=番茄&category=vegetable&page=1&pageSize=20
```

建议列表项至少包含：

```json
{
  "id": "dish-uuid",
  "legacy_id": "hoc-xxxx",
  "name": "番茄炒蛋",
  "category": "category-uuid",
  "category_name": "素菜",
  "tags": [{"id": "tag-uuid", "name": "炒"}],
  "cover_url": "/static/images/tomato-egg.png",
  "source_project": "HowToCook",
  "recipe_id": "article-uuid",
  "has_published_recipe": true,
  "like_count": 0,
  "comment_count": 0
}
```

前端只使用 `has_published_recipe=true` 的条目进入详情；没有教程的菜品可以展示但不允许进入空详情页。

### 5.2 菜品详情与教程详情

建议前端详情请求使用教程接口：

```http
GET /api/v1/recipes/:recipe_id/
```

响应中除了当前 `current_version`，还应包含用于页面头部展示的菜品信息：

```json
{
  "id": "article-uuid",
  "dish": {
    "id": "dish-uuid",
    "legacy_id": "hoc-xxxx",
    "name": "番茄炒蛋",
    "cover_url": "/static/images/tomato-egg.png",
    "category_name": "素菜",
    "tags": [{"name": "家常"}]
  },
  "title": "番茄炒蛋",
  "status": "published",
  "current_version": {
    "summary": "酸甜开胃的家常做法。",
    "cooking_minutes": 15,
    "difficulty": "basic",
    "servings": 2,
    "tips": ["鸡蛋先炒至凝固再回锅。"],
    "ingredients": [
      {"raw_text": "鸡蛋 3 个", "name": "鸡蛋", "quantity": 3, "unit": "个"}
    ],
    "steps": [
      {"description": "鸡蛋打散，锅烧热后炒至刚刚凝固。", "sort_order": 0}
    ]
  }
}
```

### 5.3 搜索协议

- 首页搜索使用后端 `search` 参数，不再在前端对完整 703 条数据重复过滤。
- 输入停止约 300ms 后发请求，连续请求只保留最后一次结果。
- 分类切换立即请求第一页。
- 翻页或滚动加载使用 `page` 和 `pageSize`。
- `results`、`count`、`next`、`previous` 由适配层统一处理，页面不直接依赖 DRF 分页格式。
- 搜索失败时显示轻量错误提示并使用最近一次缓存；首次加载失败时降级到静态数据。

## 6. `front/` 改造边界

确认实施后建议新增：

```text
front/src/
├── config/runtime.js              # API 地址和运行环境配置
├── services/http.js               # uni.request 通用封装
├── services/recipe-api.js         # 菜品、分类、教程 API
├── services/recipe-adapter.js     # API 和静态模型转换
└── utils/cache.js                 # 可选的用户端短期缓存
```

现有页面只做三类改造：

1. `index/index.vue` 将数据加载改为异步，加入 loading、错误、空结果和分页状态。
2. `detail.vue` 根据路由参数请求教程详情，保留静态 `getRecipeById` 作为失败回退。
3. `cookbook.js` 继续保留，作为离线降级数据和开发期页面占位数据，不再作为线上首选数据源。

菜品接入阶段不包含评论区和点赞按钮。账号密码身份闭环已在后续阶段增加，微信授权、短信登录和互动功能仍保持独立实施边界。

## 7. H5 与微信小程序兼容策略

统一使用 `uni.request`，不在用户端引入只适用于浏览器的 Axios。

### H5

- 开发环境：`VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`。
- 生产环境使用 HTTPS API 域名。
- 后端配置 H5 域名的 CORS。

### 微信小程序

- 真机不能请求 `127.0.0.1`，必须使用可访问的 HTTPS 域名。
- 在微信公众平台配置 `request 合法域名`。
- 开发工具可临时关闭域名校验，但不能作为生产方案。
- API 地址通过构建环境变量注入，不把开发地址写死在页面中。

### 缓存

- 分类和标签可缓存较长时间。
- 菜品列表缓存最近一次成功响应，搜索结果按 query + category 区分。
- 详情缓存短时间版本，发布新版本后由服务端响应自然更新。
- 缓存只用于提高容错，不作为用户端数据的最终事实来源。

## 8. 分阶段实施计划

### 阶段 A：后端数据和合同准备

- 增加规范化菜谱 JSON 生成流程。
- 增加 Django `import_recipes` 管理命令和导入报告。
- 导入分类、标签、703 道菜品、教程文章、版本、材料和步骤。
- 补齐公开菜品列表的 `recipe_id` 和详情接口展示字段。
- 增加后端测试：导入幂等、公开接口只返回已发布内容、搜索和分类过滤。

### 阶段 B：用户端 API 层

- 新增 `uni.request` 封装、环境配置和统一错误处理。
- 新增菜品 API 和数据适配器。
- 加入请求取消/竞态保护、分页模型和静态回退。
- 不修改现有页面视觉结构。

### 阶段 C：首页与详情页切换

- 首页接入分类、搜索和菜品列表。
- 详情页接入教程详情。
- 处理 loading、空数据、接口失败、下架和无教程状态。
- 同时验证 H5 和微信小程序构建。

### 阶段 D：灰度与清理

- 本地 API 优先、静态回退联调。
- 预发布环境验证发布/下架是否实时反映到用户端。
- 观察请求耗时、错误率和分页行为。
- 稳定后再决定是否去掉静态数据回退；不建议立即删除 `cookbook.js`。

### 阶段 E：账号密码身份闭环（已完成首版）

- `POST /api/v1/auth/register/`：账号密码注册并返回令牌。
- `POST /api/v1/auth/login/password/`：账号密码登录。
- `POST /api/v1/auth/token/refresh/`：刷新令牌前校验账号状态。
- `GET/PATCH /api/v1/users/me/`：读取和修改昵称、邮箱等资料。
- 用户端新增登录、注册和“我的”页面，请求层自动携带并刷新 JWT。
- 后台禁用或锁定账号后，登录和刷新令牌都会被拒绝。

微信小程序登录、微信手机号授权和短信验证码仍不在本阶段实现。

### 阶段 F：用户互动闭环（已完成首版）

- 菜品点赞、点踩、切换和取消，登录后可恢复当前反应状态。
- 公开评论列表、发表评论和评论赞踩。
- 新评论进入待审核状态，审核通过前不会出现在公开列表。
- 菜品与评论举报，后台沿用现有举报处理页面。
- 评论删除校验所有权，普通用户不能删除他人评论。
- 下架菜品不可评论，回复不能跨菜品，举报目标必须真实可见。
- 未登录操作统一引导账号登录，完成登录后返回原菜品详情。

## 9. 测试与验收

### 自动化

- API 适配器：完整数据、缺省字段、空列表和异常响应。
- 搜索竞态：快速连续输入时旧响应不能覆盖新结果。
- 路由兼容：旧 `legacy_id` 链接仍能打开对应详情。
- H5 构建：`npm --prefix front run build:h5`。
- 小程序构建：`npm --prefix front run build:mp-weixin`。
- 后端：导入、搜索、分类过滤、发布和下架测试。

### 手工验收

- API 返回 703 道已发布菜品时首页数量、分类和搜索结果正确。
- 后台下架一道菜后，用户端列表和详情均不再展示。
- 后台发布新教程后，用户端刷新可以看到新内容。
- H5 在 API 可用、API 失败和 API 返回空结果三种状态下均有合理界面。
- 微信开发工具和真机都能请求配置的 HTTPS API。
- 现有静态数据回退仍能打开菜品详情。

## 10. 风险与决策点

1. **数据源目录被忽略**：必须保留规范化 JSON，否则新环境无法重建数据库。
2. **ID 不兼容**：使用 `legacy_id` 保存原始 ID，并在路由适配层兼容旧链接。
3. **静态资源路径**：后端返回的封面 URL 必须能被 H5 和小程序访问；本地占位图继续由用户端提供。
4. **开发环境网络**：小程序真机不能直接访问本机 Django，需要 HTTPS 测试域名或局域网代理。
5. **发布一致性**：用户端只读 `published` 菜品和教程，草稿、待审核、下架内容不能泄露。
6. **接口性能**：搜索字段和标签关系需要数据库索引；列表接口避免逐条查询教程和标签。

## 11. 待确认事项

建议确认以下默认决策后再开始实施：

- 采用“API 优先 + 静态数据降级”，而不是一次性移除静态数据。
- 第一阶段先实现公开浏览、搜索、分类和详情，不接登录与互动。
- 将规范化 `server/data/recipes.json` 纳入 Git，原始两个上游目录继续忽略。
- 后端公开菜品列表补充 `recipe_id`，教程详情补充完整菜品展示信息。
- 首次导入的数据按已发布处理，后续新增内容遵循后台审核发布流程。
