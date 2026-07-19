<template>
  <div>
    <PageHeader title="教程内容" description="编辑教程版本并执行审核、发布和下架">
      <el-button type="primary" :icon="Plus" @click="openCreate">新建教程</el-button>
    </PageHeader>

    <div class="filter-bar">
      <el-input v-model="query.search" placeholder="搜索教程或菜品" clearable @keyup.enter="load">
        <template #prefix><Search :size="16" /></template>
      </el-input>
      <el-select v-model="query.status" placeholder="全部状态" clearable>
        <el-option label="草稿" value="draft" />
        <el-option label="待审核" value="pending_review" />
        <el-option label="已发布" value="published" />
        <el-option label="已下架" value="unpublished" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <section class="section-block" v-loading="loading">
      <el-table :data="rows" empty-text="暂无教程">
        <el-table-column prop="title" label="教程标题" min-width="220" />
        <el-table-column prop="dish_name" label="菜品" min-width="150" />
        <el-table-column label="版本" width="130">
          <template #default="scope">
            线上 v{{ scope.row.current_version?.version_no || '-' }} / 最新 v{{ scope.row.latest_version?.version_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope"><StatusTag :status="scope.row.status" /></template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="170">
          <template #default="scope">{{ formatDate(scope.row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" min-width="330" fixed="right">
          <template #default="scope">
            <div class="inline-actions">
              <el-button text :icon="Pencil" @click="openEdit(scope.row)">编辑</el-button>
              <el-button text :disabled="!scope.row.latest_version" @click="submitReview(scope.row)">提交审核</el-button>
              <el-button text type="primary" :disabled="!scope.row.latest_version" @click="publish(scope.row)">发布最新</el-button>
              <el-button v-if="scope.row.status === 'published'" text @click="unpublish(scope.row)">下架</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="query.page" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="load" />
      </div>
    </section>

    <el-dialog v-model="dialog" :title="form.id ? '编辑教程并创建新版本' : '新建教程'" width="min(860px, 94vw)" destroy-on-close>
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item label="关联菜品">
            <el-select
              v-model="form.dish"
              filterable
              remote
              :remote-method="searchDishes"
              :loading="dishLoading"
              :disabled="Boolean(form.id)"
              placeholder="输入菜名搜索"
              style="width: 100%"
              @change="fillTitle"
            >
              <el-option v-for="dish in dishOptions" :key="dish.id" :label="dish.name" :value="dish.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="教程标题"><el-input v-model="form.title" /></el-form-item>
        </div>

        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="3" maxlength="1000" show-word-limit />
        </el-form-item>

        <div class="form-grid three-columns">
          <el-form-item label="耗时（分钟）"><el-input-number v-model="form.cooking_minutes" :min="1" :max="1440" controls-position="right" /></el-form-item>
          <el-form-item label="难度">
            <el-select v-model="form.difficulty" style="width: 100%">
              <el-option label="入门" value="easy" />
              <el-option label="基础" value="basic" />
              <el-option label="进阶" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
          </el-form-item>
          <el-form-item label="份量（人）"><el-input-number v-model="form.servings" :min="1" :max="100" controls-position="right" /></el-form-item>
        </div>

        <div class="article-editor-grid">
          <el-form-item label="材料（每行一项）">
            <el-input v-model="form.ingredients" type="textarea" :rows="10" placeholder="鸡蛋 2 个&#10;番茄 2 个" />
          </el-form-item>
          <el-form-item label="步骤（每行一步）">
            <el-input v-model="form.steps" type="textarea" :rows="10" placeholder="鸡蛋打散。&#10;番茄切块。" />
          </el-form-item>
        </div>

        <el-form-item label="技巧（每行一项）">
          <el-input v-model="form.tips" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="版本说明">
          <el-input v-model="form.change_note" maxlength="240" show-word-limit placeholder="说明本次修改内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存新版本</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Pencil, Plus, Search } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatusTag from '../components/StatusTag.vue'
import { api, errorMessage, pageItems } from '../lib/api'

const rows = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const dishLoading = ref(false)
const dishOptions = ref([])
const query = reactive({ status: '', search: '', page: 1 })
const emptyForm = () => ({
  id: '',
  dish: '',
  title: '',
  summary: '',
  cooking_minutes: 20,
  difficulty: 'basic',
  servings: 1,
  ingredients: '',
  steps: '',
  tips: '',
  change_note: ''
})
const form = reactive(emptyForm())

const formatDate = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'
const lines = (value) => value.split(/\r?\n/).map((item) => item.trim()).filter(Boolean)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/articles/', { params: query })
    rows.value = pageItems(data)
    total.value = data.count ?? rows.value.length
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    loading.value = false
  }
}

async function searchDishes(search = '') {
  dishLoading.value = true
  try {
    const { data } = await api.get('/admin/dishes/', { params: { search, pageSize: 50 } })
    dishOptions.value = pageItems(data)
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    dishLoading.value = false
  }
}

function reset(values = {}) {
  Object.assign(form, emptyForm(), values)
}

function openCreate() {
  reset()
  searchDishes()
  dialog.value = true
}

function openEdit(row) {
  const version = row.latest_version || row.current_version || {}
  reset({
    id: row.id,
    dish: row.dish,
    title: row.title,
    summary: version.summary || '',
    cooking_minutes: version.cooking_minutes || 20,
    difficulty: version.difficulty || 'basic',
    servings: version.servings || 1,
    ingredients: (version.ingredients || []).map((item) => item.raw_text || item.name).join('\n'),
    steps: (version.steps || []).map((item) => item.description).join('\n'),
    tips: (version.tips || []).join('\n'),
    change_note: ''
  })
  dishOptions.value = [{ id: row.dish, name: row.dish_name }]
  dialog.value = true
}

function fillTitle(dishId) {
  if (form.title) return
  form.title = dishOptions.value.find((dish) => dish.id === dishId)?.name || ''
}

async function save() {
  const ingredients = lines(form.ingredients)
  const steps = lines(form.steps)
  if (!form.dish || !form.title || !ingredients.length || !steps.length) {
    ElMessage.warning('请填写关联菜品、标题、材料和步骤')
    return
  }
  saving.value = true
  try {
    let articleId = form.id
    if (articleId) {
      await api.patch(`/admin/articles/${articleId}/`, { title: form.title })
    } else {
      const { data } = await api.post('/admin/articles/', {
        dish: form.dish,
        title: form.title,
        status: 'draft'
      })
      articleId = data.id
    }
    await api.post(`/admin/articles/${articleId}/versions/`, {
      summary: form.summary,
      cooking_minutes: form.cooking_minutes,
      difficulty: form.difficulty,
      servings: form.servings,
      tips: lines(form.tips),
      change_note: form.change_note,
      ingredients: ingredients.map((rawText, index) => ({
        name: rawText,
        raw_text: rawText,
        sort_order: index
      })),
      steps: steps.map((description, index) => ({ description, sort_order: index }))
    })
    ElMessage.success('教程新版本已保存')
    dialog.value = false
    load()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  } finally {
    saving.value = false
  }
}

async function submitReview(row) {
  try {
    await api.post(`/admin/articles/${row.id}/submit/`)
    ElMessage.success('已提交审核')
    load()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  }
}

async function publish(row) {
  try {
    await api.post(`/admin/articles/${row.id}/publish/`, { versionId: row.latest_version.id })
    ElMessage.success('最新教程版本已发布')
    load()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  }
}

async function unpublish(row) {
  try {
    await api.post(`/admin/articles/${row.id}/unpublish/`, {})
    ElMessage.success('教程已下架')
    load()
  } catch (error) {
    ElMessage.error(errorMessage(error))
  }
}

watch(() => query.status, () => {
  query.page = 1
  load()
})
onMounted(load)
</script>

<style scoped>
.article-editor-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.three-columns { grid-template-columns: repeat(3, minmax(0, 1fr)); }
@media (max-width: 720px) {
  .article-editor-grid, .three-columns { grid-template-columns: 1fr; }
}
</style>
