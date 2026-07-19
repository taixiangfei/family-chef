<template>
  <div>
    <PageHeader title="评论审核" description="处理评论可见性和审核说明" />
    <div class="filter-bar"><el-select v-model="query.status" placeholder="全部状态" clearable><el-option label="待审核" value="pending" /><el-option label="可见" value="visible" /><el-option label="已隐藏" value="hidden" /></el-select><el-button type="primary" @click="load">查询</el-button></div>
    <section class="section-block" v-loading="loading"><el-table :data="rows" empty-text="暂无评论"><el-table-column prop="username" label="用户" width="130" /><el-table-column prop="content" label="评论内容" min-width="300" show-overflow-tooltip /><el-table-column label="状态" width="110"><template #default="s"><StatusTag :status="s.row.status" /></template></el-table-column><el-table-column label="提交时间" min-width="170"><template #default="s">{{ formatDate(s.row.created_at) }}</template></el-table-column><el-table-column label="操作" width="170"><template #default="s"><div class="inline-actions"><el-button text type="primary" @click="moderate(s.row,'visible')">通过</el-button><el-button text @click="moderate(s.row,'hidden')">隐藏</el-button></div></template></el-table-column></el-table></section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue';import { ElMessage } from 'element-plus';import PageHeader from '../components/PageHeader.vue';import StatusTag from '../components/StatusTag.vue';import { api, errorMessage, pageItems } from '../lib/api'
const rows=ref([]),loading=ref(false),query=reactive({status:'pending'}); const formatDate=(v)=>v?new Date(v).toLocaleString('zh-CN'):'-'
async function load(){loading.value=true;try{const{data}=await api.get('/admin/comments/',{params:query});rows.value=pageItems(data)}catch(e){ElMessage.error(errorMessage(e))}finally{loading.value=false}}
async function moderate(row,status){try{await api.post(`/admin/comments/${row.id}/moderate/`,{status,moderation_note:status==='visible'?'审核通过':'人工隐藏'});ElMessage.success('评论状态已更新');load()}catch(e){ElMessage.error(errorMessage(e))}}
watch(()=>query.status,load);onMounted(load)
</script>
