<template>
  <div>
    <PageHeader title="菜品管理" description="维护菜品名称、分类、标签和发布状态"><el-button type="primary" :icon="Plus" @click="openCreate">新增菜品</el-button></PageHeader>
    <div class="filter-bar"><el-input v-model="query.search" placeholder="搜索菜名、旧 ID 或来源" clearable @keyup.enter="load"><template #prefix><Search :size="16" /></template></el-input><el-select v-model="query.status" placeholder="全部状态" clearable><el-option label="草稿" value="draft" /><el-option label="已发布" value="published" /><el-option label="已下架" value="unpublished" /></el-select><el-select v-model="query.category" placeholder="全部分类" clearable><el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" /></el-select><el-button type="primary" @click="load">查询</el-button></div>
    <section class="section-block" v-loading="loading">
      <el-table :data="rows" empty-text="暂无菜品">
        <el-table-column label="菜品" min-width="220"><template #default="scope"><div class="dish-cell"><span class="dish-thumb"><Soup :size="20" /></span><div><strong>{{ scope.row.name }}</strong><small>{{ scope.row.legacy_id || scope.row.slug }}</small></div></div></template></el-table-column>
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column label="标签" min-width="180"><template #default="scope"><div class="tag-list"><el-tag v-for="tag in scope.row.tags.slice(0, 3)" :key="tag.id" size="small" effect="plain">{{ tag.name }}</el-tag><span v-if="scope.row.tags.length > 3">+{{ scope.row.tags.length - 3 }}</span></div></template></el-table-column>
        <el-table-column prop="source_project" label="来源" min-width="130"><template #default="scope">{{ scope.row.source_project || '-' }}</template></el-table-column>
        <el-table-column label="状态" width="105"><template #default="scope"><StatusTag :status="scope.row.status" /></template></el-table-column>
        <el-table-column label="更新时间" min-width="170"><template #default="scope">{{ formatDate(scope.row.updated_at) }}</template></el-table-column>
        <el-table-column label="操作" width="90" fixed="right"><template #default="scope"><el-button text :icon="Pencil" @click="openEdit(scope.row)">编辑</el-button></template></el-table-column>
      </el-table><div class="pagination"><el-pagination v-model:current-page="query.page" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="load" /></div>
    </section>
    <el-dialog v-model="dialog" :title="form.id ? '编辑菜品' : '新增菜品'" width="560px">
      <el-form label-position="top"><div class="form-grid"><el-form-item label="菜品名称"><el-input v-model="form.name" /></el-form-item><el-form-item label="英文标识"><el-input v-model="form.slug" placeholder="例如 mapo-tofu" /></el-form-item></div><div class="form-grid"><el-form-item label="分类"><el-select v-model="form.category" style="width:100%"><el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" /></el-select></el-form-item><el-form-item label="状态"><el-select v-model="form.status" style="width:100%"><el-option label="草稿" value="draft" /><el-option label="已发布" value="published" /><el-option label="已下架" value="unpublished" /></el-select></el-form-item></div><el-form-item label="标签"><el-select v-model="form.tag_ids" multiple style="width:100%"><el-option v-for="item in tags" :key="item.id" :label="item.name" :value="item.id" /></el-select></el-form-item><el-form-item label="封面地址"><el-input v-model="form.cover_url" /></el-form-item><el-form-item label="来源项目"><el-input v-model="form.source_project" /></el-form-item></el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'; import { Pencil, Plus, Search, Soup } from 'lucide-vue-next'; import { ElMessage } from 'element-plus'; import PageHeader from '../components/PageHeader.vue'; import StatusTag from '../components/StatusTag.vue'; import { api, errorMessage, pageItems } from '../lib/api'
const rows=ref([]), categories=ref([]), tags=ref([]), total=ref(0), loading=ref(false), saving=ref(false), dialog=ref(false); const query=reactive({search:'',status:'',category:'',page:1}); const empty=()=>({id:'',name:'',slug:'',category:'',tag_ids:[],cover_url:'',status:'draft',source_project:''}); const form=reactive(empty())
const formatDate=(v)=>v?new Date(v).toLocaleString('zh-CN'):'-'; async function loadOptions(){ const [c,t]=await Promise.all([api.get('/admin/categories/',{params:{pageSize:100}}),api.get('/admin/tags/',{params:{pageSize:100}})]); categories.value=pageItems(c.data); tags.value=pageItems(t.data) }
async function load(){loading.value=true;try{const{data}=await api.get('/admin/dishes/',{params:query});rows.value=pageItems(data);total.value=data.count??rows.value.length}catch(e){ElMessage.error(errorMessage(e))}finally{loading.value=false}}
function reset(values={}){Object.assign(form,empty(),values)} function openCreate(){reset();dialog.value=true} function openEdit(row){reset({...row,tag_ids:row.tags.map(t=>t.id)});dialog.value=true}
async function save(){if(!form.name||!form.slug||!form.category){ElMessage.warning('请填写名称、标识和分类');return} saving.value=true;const payload={legacy_id:form.legacy_id||null,name:form.name,slug:form.slug,category:form.category,tag_ids:form.tag_ids,cover_url:form.cover_url,status:form.status,source_project:form.source_project,source_path:form.source_path||'',source_url:form.source_url||''};try{form.id?await api.patch(`/admin/dishes/${form.id}/`,payload):await api.post('/admin/dishes/',payload);ElMessage.success('菜品已保存');dialog.value=false;load()}catch(e){ElMessage.error(errorMessage(e))}finally{saving.value=false}}
watch(()=>[query.status,query.category],()=>{query.page=1;load()});onMounted(async()=>{try{await loadOptions()}catch(e){ElMessage.error(errorMessage(e))}load()})
</script>
