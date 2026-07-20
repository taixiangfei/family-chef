import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '../lib/auth'
import AppLayout from '../layouts/AppLayout.vue'
import LoginPage from '../views/LoginPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import UsersPage from '../views/UsersPage.vue'
import DishesPage from '../views/DishesPage.vue'
import TaxonomyPage from '../views/TaxonomyPage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import CommentsPage from '../views/CommentsPage.vue'
import ReportsPage from '../views/ReportsPage.vue'
import MealPlansPage from '../views/MealPlansPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage, meta: { public: true } },
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardPage, meta: { title: '工作台' } },
        { path: 'users', name: 'users', component: UsersPage, meta: { title: '用户管理' } },
        { path: 'dishes', name: 'dishes', component: DishesPage, meta: { title: '菜品管理' } },
        { path: 'taxonomy', name: 'taxonomy', component: TaxonomyPage, meta: { title: '分类与标签' } },
        { path: 'articles', name: 'articles', component: ArticlesPage, meta: { title: '教程内容' } },
        { path: 'meal-plans', name: 'meal-plans', component: MealPlansPage, meta: { title: '配菜方案' } },
        { path: 'comments', name: 'comments', component: CommentsPage, meta: { title: '评论审核' } },
        { path: 'reports', name: 'reports', component: ReportsPage, meta: { title: '举报处理' } }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach((to) => {
  if (!to.meta.public && !authState.access) return '/login'
  if (to.path === '/login' && authState.access) return '/'
})

export default router
