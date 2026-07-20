<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ collapsed }">
      <div class="brand">
        <div class="brand-mark"><ChefHat :size="22" /></div>
        <div v-if="!collapsed" class="brand-copy">
          <strong>家常主厨</strong>
          <span>内容管理台</span>
        </div>
      </div>

      <nav class="nav-list" aria-label="管理导航">
        <router-link v-for="item in menu" :key="item.path" :to="item.path" class="nav-item">
          <component :is="item.icon" :size="18" />
          <span v-if="!collapsed">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-foot">
        <button class="collapse-button" type="button" :title="collapsed ? '展开侧栏' : '收起侧栏'" @click="collapsed = !collapsed">
          <PanelLeftClose v-if="!collapsed" :size="18" />
          <PanelLeftOpen v-else :size="18" />
          <span v-if="!collapsed">收起侧栏</span>
        </button>
      </div>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <div>
          <p class="breadcrumb">家常主厨 / 管理中心</p>
          <h1>{{ route.meta.title }}</h1>
        </div>
        <div class="topbar-actions">
          <a class="icon-link" :href="docsUrl" target="_blank" title="API 文档"><BookOpen :size="18" /></a>
          <el-dropdown trigger="click" @command="handleCommand">
            <button class="profile-button" type="button">
              <span class="avatar">{{ initial }}</span>
              <span class="profile-copy">
                <strong>{{ authState.user?.nickname || authState.user?.username || '管理员' }}</strong>
                <small>后台管理员</small>
              </span>
              <ChevronDown :size="15" />
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="django">Django Admin</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <div class="content-area"><router-view /></div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  BookOpen,
  ChefHat,
  ChevronDown,
  CircleAlert,
  FileText,
  FolderTree,
  LayoutDashboard,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  Soup,
  Users
} from 'lucide-vue-next'
import { authState, clearAuth } from '../lib/auth'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const docsUrl = import.meta.env.VITE_API_DOCS_URL || 'http://127.0.0.1:8000/api/docs/'
const djangoAdminUrl = import.meta.env.VITE_DJANGO_ADMIN_URL || 'http://127.0.0.1:8000/django-admin/'
const initial = computed(() => (authState.user?.nickname || authState.user?.username || '管').slice(0, 1))
const menu = [
  { path: '/', label: '工作台', icon: LayoutDashboard },
  { path: '/users', label: '用户管理', icon: Users },
  { path: '/dishes', label: '菜品管理', icon: Soup },
  { path: '/taxonomy', label: '分类与标签', icon: FolderTree },
  { path: '/articles', label: '教程内容', icon: FileText },
  { path: '/comments', label: '评论审核', icon: MessageSquare },
  { path: '/reports', label: '举报处理', icon: CircleAlert }
]

function handleCommand(command) {
  if (command === 'django') window.open(djangoAdminUrl, '_blank')
  if (command === 'logout') {
    clearAuth()
    router.replace('/login')
  }
}
</script>
