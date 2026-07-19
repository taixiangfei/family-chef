<template>
  <div>
    <PageHeader title="用户管理" description="查看用户身份、状态与后台权限" />
    <div class="filter-bar">
      <el-input v-model="query.search" placeholder="搜索账号、昵称或邮箱" clearable @keyup.enter="load"><template #prefix><Search :size="16" /></template></el-input>
      <el-select v-model="query.status" placeholder="全部状态" clearable><el-option v-for="item in statuses" :key="item.value" :label="item.label" :value="item.value" /></el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <section class="section-block" v-loading="loading">
      <el-table :data="rows" empty-text="暂无用户">
        <el-table-column label="用户" min-width="190"><template #default="scope"><div class="identity-cell"><span class="table-avatar">{{ (scope.row.nickname || scope.row.username)[0] }}</span><div><strong>{{ scope.row.nickname || scope.row.username }}</strong><small>@{{ scope.row.username }}</small></div></div></template></el-table-column>
        <el-table-column prop="phone" label="手机号" min-width="130"><template #default="scope">{{ scope.row.phone || '-' }}</template></el-table-column>
        <el-table-column label="角色" min-width="150"><template #default="scope"><span v-if="scope.row.is_superuser">超级管理员</span><span v-else-if="scope.row.roles.length">{{ scope.row.roles.join('、') }}</span><span v-else>普通用户</span></template></el-table-column>
        <el-table-column label="状态" width="110"><template #default="scope"><StatusTag :status="scope.row.status" /></template></el-table-column>
        <el-table-column label="注册时间" min-width="170"><template #default="scope">{{ formatDate(scope.row.date_joined) }}</template></el-table-column>
        <el-table-column label="操作" width="130" fixed="right"><template #default="scope"><el-dropdown @command="(value) => changeStatus(scope.row, value)"><el-button text>修改状态<ChevronDown :size="14" /></el-button><template #dropdown><el-dropdown-menu><el-dropdown-item command="active">设为正常</el-dropdown-item><el-dropdown-item command="disabled">禁用账号</el-dropdown-item><el-dropdown-item command="locked">锁定账号</el-dropdown-item></el-dropdown-menu></template></el-dropdown></template></el-table-column>
      </el-table>
      <div class="pagination"><el-pagination v-model:current-page="query.page" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="load" /></div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ChevronDown, Search } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'; import StatusTag from '../components/StatusTag.vue'; import { api, errorMessage, pageItems } from '../lib/api'
const rows = ref([]), total = ref(0), loading = ref(false); const query = reactive({ search: '', status: '', page: 1 })
const statuses = [{ value: 'active', label: '正常' }, { value: 'disabled', label: '已禁用' }, { value: 'locked', label: '已锁定' }]
const formatDate = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'
async function load() { loading.value = true; try { const { data } = await api.get('/admin/users/', { params: query }); rows.value = pageItems(data); total.value = data.count ?? rows.value.length } catch (e) { ElMessage.error(errorMessage(e)) } finally { loading.value = false } }
async function changeStatus(row, status) { try { await api.patch(`/admin/users/${row.id}/status/`, { status }); ElMessage.success('用户状态已更新'); load() } catch (e) { ElMessage.error(errorMessage(e)) } }
watch(() => query.status, () => { query.page = 1; load() }); onMounted(load)
</script>
