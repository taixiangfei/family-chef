<template>
  <div>
    <PageHeader title="配菜方案" description="维护搭配主题，并查看用户生成与保存的方案" />
    <el-tabs v-model="active" class="section-block">
      <el-tab-pane label="主题模板" name="templates">
        <div class="table-tools">
          <el-input v-model="templateSearch" placeholder="搜索主题" clearable><template #prefix><Search :size="16" /></template></el-input>
          <el-button type="primary" :icon="Plus" @click="openTemplate()">新增主题</el-button>
        </div>
        <el-table :data="filteredTemplates" v-loading="templatesLoading" empty-text="暂无主题">
          <el-table-column prop="name" label="主题名称" width="150" />
          <el-table-column prop="key" label="标识" width="150" />
          <el-table-column prop="description" label="说明" min-width="240" show-overflow-tooltip />
          <el-table-column prop="sort_order" label="排序" width="90" />
          <el-table-column label="状态" width="110"><template #default="s"><StatusTag :status="s.row.status" /></template></el-table-column>
          <el-table-column label="操作" width="90"><template #default="s"><el-button text :icon="Pencil" @click="openTemplate(s.row)">编辑</el-button></template></el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="方案列表" name="plans">
        <div class="table-tools">
          <el-input v-model="planSearch" placeholder="搜索标题或用户" clearable><template #prefix><Search :size="16" /></template></el-input>
          <el-select v-model="planStatus" clearable placeholder="状态" style="width:140px"><el-option label="临时" value="draft" /><el-option label="已保存" value="saved" /><el-option label="已归档" value="archived" /></el-select>
        </div>
        <el-table :data="plans" v-loading="plansLoading" empty-text="暂无方案">
          <el-table-column prop="title" label="方案" min-width="180" />
          <el-table-column prop="username" label="用户" width="140" />
          <el-table-column label="方式" width="110"><template #default="s">{{ modeLabels[s.row.mode] || s.row.mode }}</template></el-table-column>
          <el-table-column prop="themeKey" label="主题" width="120" />
          <el-table-column prop="targetCount" label="菜数" width="90" />
          <el-table-column prop="totalMinutes" label="耗时" width="90" />
          <el-table-column label="状态" width="110"><template #default="s"><StatusTag :status="s.row.status" /></template></el-table-column>
          <el-table-column label="操作" width="90"><template #default="s"><el-button text @click="openPlan(s.row)">查看</el-button></template></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="templateDialog" :title="`${editing.id ? '编辑' : '新增'}主题`" width="560px">
      <el-form label-position="top">
        <el-form-item label="主题名称"><el-input v-model="editing.name" /></el-form-item>
        <el-form-item label="主题标识"><el-input v-model="editing.key" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="editing.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="规则 JSON"><el-input v-model="rulesText" type="textarea" :rows="7" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="editing.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="editing.status"><el-radio-button value="active">启用</el-radio-button><el-radio-button value="disabled">停用</el-radio-button></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="templateDialog=false">取消</el-button><el-button type="primary" @click="saveTemplate">保存</el-button></template>
    </el-dialog>

    <el-drawer v-model="planDrawer" title="方案详情" size="520px">
      <div v-if="currentPlan" class="plan-detail">
        <h3>{{ currentPlan.title }}</h3>
        <p>{{ currentPlan.summary }}</p>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户">{{ currentPlan.username || '匿名' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentPlan.status }}</el-descriptions-item>
          <el-descriptions-item label="人数">{{ currentPlan.servings }}</el-descriptions-item>
          <el-descriptions-item label="菜数">{{ currentPlan.items.length }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <el-timeline>
          <el-timeline-item v-for="item in currentPlan.items" :key="item.id" :timestamp="`${item.cookingMinutes || '-'} 分钟`">
            <strong>{{ item.name }}</strong>
            <p>{{ item.reason }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Pencil, Plus, Search } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatusTag from '../components/StatusTag.vue'
import { api, errorMessage, pageItems } from '../lib/api'

const active=ref('templates'),templates=ref([]),plans=ref([]),templateSearch=ref(''),planSearch=ref(''),planStatus=ref(''),templatesLoading=ref(false),plansLoading=ref(false),templateDialog=ref(false),planDrawer=ref(false),rulesText=ref('{}'),currentPlan=ref(null)
const editing=reactive({id:'',key:'',name:'',description:'',rules:{},sort_order:0,status:'active'})
const modeLabels={custom:'自定义',theme:'主题',random:'随机'}
const filteredTemplates=computed(()=>templates.value.filter(item=>`${item.name}${item.key}`.includes(templateSearch.value)))

async function loadTemplates(){templatesLoading.value=true;try{const{data}=await api.get('/admin/meal-plan-templates/',{params:{pageSize:100}});templates.value=pageItems(data)}catch(e){ElMessage.error(errorMessage(e))}finally{templatesLoading.value=false}}
async function loadPlans(){plansLoading.value=true;try{const params={pageSize:50,search:planSearch.value,status:planStatus.value};const{data}=await api.get('/admin/meal-plans/',{params});plans.value=pageItems(data)}catch(e){ElMessage.error(errorMessage(e))}finally{plansLoading.value=false}}
function openTemplate(row={}){Object.assign(editing,{id:'',key:'',name:'',description:'',rules:{},sort_order:0,status:'active'},row);rulesText.value=JSON.stringify(editing.rules || {}, null, 2);templateDialog.value=true}
async function saveTemplate(){let rules;try{rules=JSON.parse(rulesText.value || '{}')}catch{ElMessage.error('规则 JSON 格式不正确');return}const payload={key:editing.key,name:editing.name,description:editing.description,rules,sort_order:editing.sort_order,status:editing.status};try{editing.id?await api.patch(`/admin/meal-plan-templates/${editing.id}/`,payload):await api.post('/admin/meal-plan-templates/',payload);ElMessage.success('主题已保存');templateDialog.value=false;loadTemplates()}catch(e){ElMessage.error(errorMessage(e))}}
function openPlan(row){currentPlan.value=row;planDrawer.value=true}
watch([planSearch,planStatus],()=>loadPlans())
onMounted(()=>{loadTemplates();loadPlans()})
</script>

<style scoped>
.plan-detail h3 { margin: 0 0 10px; color: #1f2933; }
.plan-detail p { color: #667085; line-height: 1.55; }
</style>
