<template>
  <div>
    <PageHeader title="举报处理" description="跟进用户反馈并记录处理结果" />
    <section class="section-block" v-loading="loading"><el-table :data="rows" empty-text="暂无举报"><el-table-column prop="reporter_name" label="举报人" width="140" /><el-table-column label="目标类型" width="110"><template #default="s">{{ targetLabels[s.row.target_type] || s.row.target_type }}</template></el-table-column><el-table-column prop="reason" label="原因" width="140" /><el-table-column prop="description" label="说明" min-width="260" show-overflow-tooltip /><el-table-column label="状态" width="110"><template #default="s"><StatusTag :status="s.row.status" /></template></el-table-column><el-table-column label="操作" width="180"><template #default="s"><div class="inline-actions"><el-button text type="primary" @click="resolve(s.row,'resolved')">处理完成</el-button><el-button text @click="resolve(s.row,'dismissed')">驳回</el-button></div></template></el-table-column></el-table></section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';import { ElMessage } from 'element-plus';import PageHeader from '../components/PageHeader.vue';import StatusTag from '../components/StatusTag.vue';import { api, errorMessage, pageItems } from '../lib/api'
const rows=ref([]),loading=ref(false),targetLabels={dish:'菜品',comment:'评论'}; async function load(){loading.value=true;try{const{data}=await api.get('/reports/');rows.value=pageItems(data)}catch(e){ElMessage.error(errorMessage(e))}finally{loading.value=false}}
async function resolve(row,status){try{await api.post(`/reports/${row.id}/resolve/`,{status,resolution:status==='resolved'?'已处理并记录':'经核查不成立'});ElMessage.success('举报状态已更新');load()}catch(e){ElMessage.error(errorMessage(e))}} onMounted(load)
</script>
