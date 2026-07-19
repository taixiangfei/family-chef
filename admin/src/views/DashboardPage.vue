<template>
  <div v-loading="loading">
    <PageHeader title="工作台" description="内容、用户和社区状态概览">
      <el-button :icon="RefreshCw" @click="load">刷新</el-button>
    </PageHeader>
    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <div class="metric-grid">
      <article v-for="metric in metrics" :key="metric.key" class="metric-card">
        <div class="metric-icon" :class="metric.tone"><component :is="metric.icon" :size="20" /></div>
        <div><span>{{ metric.label }}</span><strong>{{ stats[metric.key] ?? 0 }}</strong></div>
      </article>
    </div>
    <section class="section-block">
      <div class="section-heading"><div><h3>最近更新的菜品</h3><p>按最近编辑时间排列</p></div><router-link to="/dishes">查看全部</router-link></div>
      <el-table :data="recentDishes" empty-text="暂无菜品数据">
        <el-table-column prop="name" label="菜品" min-width="180" />
        <el-table-column prop="category__name" label="分类" min-width="120" />
        <el-table-column label="状态" width="110"><template #default="scope"><StatusTag :status="scope.row.status" /></template></el-table-column>
        <el-table-column label="更新时间" min-width="170"><template #default="scope">{{ formatDate(scope.row.updated_at) }}</template></el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { CircleAlert, FileClock, MessageSquare, RefreshCw, Soup, Users } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatusTag from '../components/StatusTag.vue'
import { api, errorMessage } from '../lib/api'

const loading = ref(false), error = ref(''), data = ref({ stats: {}, recentDishes: [] })
const stats = computed(() => data.value.stats || {})
const recentDishes = computed(() => data.value.recentDishes || [])
const metrics = [
  { key: 'users', label: '用户总数', icon: Users, tone: 'green' },
  { key: 'dishes', label: '菜品总数', icon: Soup, tone: 'red' },
  { key: 'pendingArticles', label: '待审核教程', icon: FileClock, tone: 'blue' },
  { key: 'pendingComments', label: '待审核评论', icon: MessageSquare, tone: 'amber' },
  { key: 'pendingReports', label: '待处理举报', icon: CircleAlert, tone: 'gray' }
]
const formatDate = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'
async function load() { loading.value = true; error.value = ''; try { data.value = (await api.get('/admin/dashboard/')).data } catch (e) { error.value = errorMessage(e) } finally { loading.value = false } }
onMounted(load)
</script>
