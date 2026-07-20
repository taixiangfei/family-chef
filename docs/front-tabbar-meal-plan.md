# 用户端 TabBar 与配菜方案功能规划

> 版本：v0.1
> 日期：2026-07-20
> 状态：已完成首版实施
> 范围：`front/` 用户端、`server/` 后端、`admin/` 管理端

> 实施记录：已新增用户端底部 TabBar、配菜方案生成/详情/保存、我的评论/举报/配菜方案列表；
> 后端已新增 `meal_plans` 业务模块、规则生成服务、公开与个人接口；管理端已新增配菜方案入口、
> 主题模板管理和方案查看。

## 1. 目标

把当前用户端从“首页 + 详情 + 登录/个人页”的导航结构，升级为底部
TabBar 模式：

- 首页：保留当前菜谱搜索、分类筛选、随机菜谱和详情能力。
- 配菜方案：支持自定义、主题和随机三种方式生成一组菜品搭配。
- 我的：集中承载登录/退出、个人资料、我的评论、我的举报、我的配菜方案。

后端同步增加配菜方案业务模块，提供方案生成、保存、查询和管理能力。微信登录、微信手机号授权和短信验证码仍暂缓，不纳入本次实施。

## 2. 产品形态

### 2.1 底部 TabBar

使用 uni-app 原生 `tabBar`，保证 H5 和微信小程序行为一致。

```text
首页        pages/index/index
配菜方案    pages/meal-plan/index
我的        pages/profile/index
```

导航调整：

- 菜品详情继续使用 `uni.navigateTo`，不放入 TabBar。
- 登录、注册继续作为普通页面，不放入 TabBar。
- 首页右上角“登录/我的”入口可以保留为轻入口，但主要入口迁移到底部“我的”。
- 从登录成功返回时，如果来源是 TabBar 页面，使用 `uni.switchTab`；如果来源是详情页，使用 `uni.redirectTo` 或 `uni.navigateBack`。

TabBar 样式建议：

- 主色延续当前 `#254f47`。
- 背景使用 `#fffaf2` 或接近当前页面底色。
- 图标先用本地静态图标或 uni-app 支持的图片资源；不依赖只适用于 H5 的图标库。

### 2.2 首页

首页作为现有能力的稳定入口，本次只做导航适配：

- 保留现有搜索、分类、菜品列表、加载更多、随机菜谱。
- 首页内容不因 TabBar 改造改变数据来源。
- 页面底部增加 TabBar 后，需要补足安全区和底部留白，避免列表内容被遮挡。

### 2.3 配菜方案

配菜方案页提供三种生成方式：

1. 自定义搭配
   用户选择人数、餐次、目标菜数、偏好分类、忌口关键词、已有食材和期望耗时，系统从已发布菜品中生成方案。

2. 主题搭配
   提供预设主题，例如：
   - 营养均衡
   - 减脂轻食
   - 下饭家常
   - 快手晚餐
   - 一人食
   - 宴客硬菜

3. 随机搭配
   用户只选择人数和菜数，后端按基础规则随机生成，适合“不知道吃什么”的场景。

生成结果建议包含：

- 方案标题和主题。
- 菜品列表，每道菜展示名称、分类、标签、耗时、难度、封面和进入教程按钮。
- 总耗时估算。
- 口味/做法分布提示，例如“2 道快手菜、1 道汤、1 道荤菜”。
- 材料清单，按原菜谱材料原文聚合展示。
- 可替换单道菜、重新生成、保存方案。

首版生成规则不引入 AI，先用可解释的规则引擎完成：

- 只使用 `published` 菜品和已发布教程。
- 按分类和标签做候选池筛选。
- 优先保证菜品分类/做法不过度重复。
- 减脂主题降低高油炸、重口味标签权重。
- 快手主题优先 `cooking_minutes <= 30`。
- 宴客主题优先难度较高或标签更完整的菜。
- 忌口关键词匹配菜名、标签和材料原文，命中则排除。
- 已有食材命中材料原文时提升权重。

后续可以在规则引擎稳定后，再增加“AI 解释搭配原因”或“智能购物清单”。

### 2.4 我的

“我的”作为 TabBar 页面，未登录和已登录展示不同状态。

未登录：

- 显示登录/注册入口。
- 不阻断浏览首页和配菜方案生成。
- 保存方案、发表评论、举报、查看个人记录时引导登录。

已登录：

- 个人资料：复用现有资料读取和修改。
- 退出登录：清理 token 后 `uni.switchTab` 到首页或停留在我的。
- 我的评论：展示自己发表的评论，包括待审核、可见、隐藏、已删除等状态。
- 我的举报：展示自己提交的举报和处理状态。
- 我的配菜方案：展示保存过的方案，支持查看、删除、再次生成类似方案。

## 3. 后端设计

### 3.1 新增 Django app

新增：

```text
server/apps/meal_plans/
├── models.py
├── serializers.py
├── services.py
├── views.py
├── urls.py
├── admin.py
├── tests.py
└── migrations/
```

`services.py` 放生成算法，避免把搭配逻辑堆在 ViewSet 中。

### 3.2 数据模型

#### MealPlanTemplate

后台维护主题模板。

| 字段 | 说明 |
| --- | --- |
| `key` | 主题唯一键，例如 `balanced`、`fat_loss` |
| `name` | 主题名称 |
| `description` | 主题说明 |
| `rules` | JSON 规则，例如分类权重、标签偏好、耗时范围 |
| `status` | 启用/停用 |
| `sort_order` | 排序 |

#### MealPlan

用户生成或保存的方案。

| 字段 | 说明 |
| --- | --- |
| `user` | 可为空，未登录生成的临时方案不落库或匿名落库 |
| `title` | 方案标题 |
| `mode` | `custom`、`theme`、`random` |
| `theme_key` | 主题键，可为空 |
| `servings` | 人数 |
| `meal_type` | `breakfast`、`lunch`、`dinner`、`all_day` 等 |
| `target_count` | 目标菜数 |
| `preferences` | JSON，保存用户输入偏好 |
| `summary` | 方案摘要 |
| `total_minutes` | 总耗时估算 |
| `shopping_list` | JSON，首版保留原材料文本分组 |
| `status` | `draft`、`saved`、`archived` |

#### MealPlanItem

方案中的菜品条目。

| 字段 | 说明 |
| --- | --- |
| `plan` | 所属方案 |
| `dish` | 对应菜品 |
| `recipe` | 对应已发布教程 |
| `sort_order` | 排序 |
| `reason` | 入选原因 |
| `snapshot` | JSON，保存生成时的菜名、标签、封面、耗时，避免后续菜品变更导致历史方案完全变样 |

### 3.3 API 设计

公开接口：

```http
GET  /api/v1/meal-plan-themes/
POST /api/v1/meal-plans/generate/
GET  /api/v1/meal-plans/:id/
```

登录后接口：

```http
GET    /api/v1/users/me/meal-plans/
POST   /api/v1/meal-plans/:id/save/
DELETE /api/v1/meal-plans/:id/
POST   /api/v1/meal-plans/:id/regenerate/
POST   /api/v1/meal-plans/:id/items/:item_id/replace/
```

我的页面补充接口：

```http
GET /api/v1/users/me/comments/
GET /api/v1/users/me/reports/
```

生成请求示例：

```json
{
  "mode": "theme",
  "themeKey": "fat_loss",
  "servings": 2,
  "mealType": "dinner",
  "targetCount": 4,
  "categoryKeys": ["meat_dish", "vegetable_dish", "soup"],
  "avoidKeywords": ["香菜", "内脏"],
  "availableIngredients": ["鸡胸肉", "西兰花", "鸡蛋"],
  "maxMinutes": 45
}
```

响应示例：

```json
{
  "id": "uuid",
  "title": "减脂晚餐 4 菜方案",
  "mode": "theme",
  "themeKey": "fat_loss",
  "servings": 2,
  "targetCount": 4,
  "totalMinutes": 70,
  "summary": "整体偏清淡，优先使用高蛋白和蔬菜类菜品。",
  "items": [
    {
      "id": "uuid",
      "dishId": "uuid",
      "recipeId": "uuid",
      "name": "西兰花炒鸡胸肉",
      "categoryName": "荤菜",
      "coverUrl": "",
      "cookingMinutes": 25,
      "difficulty": "basic",
      "tags": ["快手", "减脂"],
      "reason": "匹配已有食材鸡胸肉，并符合减脂主题。"
    }
  ],
  "shoppingList": [
    { "name": "西兰花", "items": ["西兰花 1 棵"] }
  ],
  "isSaved": false
}
```

### 3.4 权限策略

- 生成方案允许匿名访问，但匿名方案默认不进入“我的”。
- 保存方案、删除方案、查看自己的历史方案需要登录。
- 用户只能查看、删除自己的方案。
- 管理员可在管理端查看全部方案，用于排查和运营分析。
- 菜品下架后，不再被新方案选中；历史方案保留快照，但进入教程时提示菜品已下架。

### 3.5 管理端补充

`admin/` 增加“配菜方案”管理入口：

- 主题模板管理：新增、编辑、启停、排序、规则 JSON。
- 方案列表：按用户、主题、生成方式、时间筛选。
- 方案详情：查看入选菜品、生成参数、购物清单和用户保存状态。
- 运营统计：主题使用次数、保存率、常被替换菜品。

首版可以先实现主题模板 CRUD 和方案只读列表，统计留到后续。

## 4. 用户端实施范围

### 4.1 新增/调整页面

```text
front/src/pages.json
front/src/pages/index/index.vue
front/src/pages/meal-plan/index.vue
front/src/pages/meal-plan/detail.vue
front/src/pages/profile/index.vue
front/src/pages/profile/comments.vue
front/src/pages/profile/reports.vue
front/src/pages/profile/meal-plans.vue
```

### 4.2 新增服务层

```text
front/src/services/meal-plan-api.js
front/src/services/profile-api.js
```

`meal-plan-api.js` 负责主题、生成、保存、替换和删除。
`profile-api.js` 负责我的评论、我的举报、我的配菜方案。

### 4.3 页面交互

配菜方案首页：

- 顶部为模式切换：主题、自定义、随机。
- 主题模式展示主题列表和基础参数。
- 自定义模式展示偏好表单。
- 随机模式保留最少输入。
- 生成中显示加载状态，失败时给出明确提示。
- 生成成功后进入方案详情。

方案详情：

- 展示菜品卡片、材料清单、总耗时、保存按钮。
- 单道菜可替换。
- 点击菜品进入现有菜谱详情。
- 未登录点击保存时跳转登录，登录后回到当前方案详情。

我的：

- 未登录显示登录/注册入口。
- 已登录显示资料编辑、退出登录，以及三个列表入口：评论、举报、配菜方案。
- 各列表使用分页加载，空状态给出简洁反馈。

## 5. 分阶段实施计划

### 阶段 A：后端配菜方案基础

- 新增 `meal_plans` app、模型、迁移和 Django Admin。
- 增加主题模板 seed 或迁移初始化数据。
- 实现规则生成服务。
- 实现主题列表、方案生成、方案详情、保存、删除接口。
- 增加后端测试：匿名生成、登录保存、权限隔离、下架菜品不参与生成。

### 阶段 B：我的相关接口

- 增加 `GET /users/me/comments/`。
- 增加 `GET /users/me/reports/`。
- 增加 `GET /users/me/meal-plans/`。
- 调整序列化字段，保证用户端能展示状态、时间、目标内容摘要。
- 增加测试：用户只能看到自己的评论、举报和方案。

### 阶段 C：用户端 TabBar

- 修改 `pages.json`，加入原生 `tabBar`。
- 新增配菜方案 Tab 页面。
- 调整 profile 为 Tab 页面，去掉不适合 Tab 页的返回按钮。
- 修正登录后返回 TabBar 页的跳转逻辑。
- 检查 H5 和微信小程序的底部安全区。

### 阶段 D：用户端配菜方案闭环

- 接入主题、生成、详情、保存、删除、替换接口。
- 增加未登录保存引导。
- 增加 API 失败时的轻量错误提示。
- 与现有菜谱详情打通。

### 阶段 E：管理端补充

- 增加配菜方案菜单。
- 实现主题模板 CRUD。
- 实现方案只读列表和详情。

### 阶段 F：验证

- 后端：pytest、ruff、Django check、makemigrations --check。
- 用户端：H5 构建、微信小程序构建。
- 管理端：生产构建。
- 手工联调：匿名生成、登录保存、我的方案、我的评论、我的举报、下架菜品不出现在新方案。

## 6. 风险与取舍

- 当前材料仍以 `raw_text` 为主，购物清单首版只能做轻量聚合，不能保证同名食材完全合并。
- 规则生成适合首版闭环，但不是营养学建议，页面不应包装成医疗或专业营养方案。
- 真实图片资源不足，方案页先复用菜品封面和现有占位图。
- 匿名生成若全部落库会产生垃圾数据，首版建议匿名生成只返回结果；用户保存时再落库。
- TabBar 页面不能用 `navigateTo` 打开，需要使用 `switchTab`，登录回跳逻辑要单独处理。

## 7. 推荐确认点

建议首版按以下边界实施：

- 只做账号密码登录下的保存和个人记录，不做微信/短信。
- 配菜方案生成采用规则引擎，不接 AI。
- 匿名用户可以生成，但不能保存。
- 管理端首版只做主题模板管理和方案查看。
- “我的评论”和“我的举报”先做只读列表，不在列表页内提供复杂审核或撤回流程。
