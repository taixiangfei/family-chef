# 家常主厨管理端

基于 Vue 3、Vite 和 Element Plus 的独立 Web 管理台，通过 JWT 调用
`server/` 提供的 API，不依赖也不修改 `front/`。

## 本地启动

先启动后端，再执行：

```bash
npm install
npm run dev -- --host 127.0.0.1
```

管理台默认地址为 `http://127.0.0.1:5174/`。登录账号需由 Django
`createsuperuser` 创建并具备 `is_staff` 权限。

## 构建

```bash
npm run build
```

接口地址、Django Admin 和 API 文档地址可按 `.env.example` 配置。
