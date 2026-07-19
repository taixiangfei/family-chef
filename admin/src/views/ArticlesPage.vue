<template>
  <div>
    <PageHeader title="教程内容" description="查看教程状态并执行提交、发布、下架动作" />
    <div class="filter-bar"><el-select v-model="query.status" placeholder="全部状态" clearable><el-option label="草稿" value="draft" /><el-option label="待审核" value="pending_review" /><el-option label="已发布" value="published" /><el-option label="已下架" value="unpublished" /></el-select><el-button type="primary" @click="load">查询</el-button></div>
    <section class="section-block" v-loading="loading"><el-table :data="rows" empty-text="暂无教程"><el-table-column prop="title" label="教程标题" min-width="220" /><el-table-column prop="dish_name" label="菜品" min-width="160" /><el-table-column prop="version_count" label="版本数" width="90" /><el-table-column label="状态" width="110"><template #default="s"><StatusTag :status="s.row.status" /></template></el-table-column><el-table-column label="当前版本" min-width="120"><template #default="s">v{{ s.row.current_version?.version_no || '-' }}</template></el-table-column><el-table-column label="操作" min-width="260" fixed="right"><template #default="s"><div class="inline-actions"><el-button text @click="submitReview(s.row)">提交审核</el-button><el-button text type="primary" @click="publish(s.row)">发布</el-button><el-button text @click="unpublish(s.row)">下架</el-button></div></template></el-table-column></el-table></section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue';import { ElMessage } from 'element-plus';import PageHeader from '../components/PageHeader.vue';import StatusTag from '../components/StatusTag.vue';import { api, errorMessage, pageItems } from '../lib/api'
const rows=ref([]),loading=ref(false),query=reactive({status:''}); async function load(){loading.value=true;try{const{data}=await api.get('/admin/articles/',{params:query});rows.value=pageItems(data)}catch(e){ElMessage.error(errorMessage(e))}finally{loading.value=false}}
async function submitReview(row){try{await api.post(`/admin/articles/${row.id}/submit/`);ElMessage.success('已提交审核');load()}catch(e){ElMessage.error(errorMessage(e))}}
async function publish(row){try{await api.post(`/admin/articles/${row.id}/publish/`,{});ElMessage.success('教程已发布');load()}catch(e){ElMessage.error(errorMessage(e))}}
async function unpublish(row){try{await api.post(`/admin/articles/${row.id}/unpublish/`,{});ElMessage.success('教程已下架');load()}catch(e){ElMessage.error(errorMessage(e))}}
watch(()=>query.status,load);onMounted(load)
</script>
