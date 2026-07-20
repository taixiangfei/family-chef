<template>
  <view class="plan-page">
    <view class="hero">
      <text class="eyebrow">Meal Plan</text>
      <text class="title">今天这样搭</text>
      <text class="subtitle">按主题、偏好或随机方式，从已发布菜谱里搭一桌可执行的方案。</text>
    </view>

    <view class="mode-tabs">
      <button v-for="item in modes" :key="item.key" class="mode-tab" :class="{ active: mode === item.key }" @tap="mode = item.key">
        {{ item.label }}
      </button>
    </view>

    <view v-if="mode === 'theme'" class="panel">
      <text class="panel-title">主题</text>
      <view v-if="themesLoading" class="status">正在加载主题...</view>
      <view v-else class="theme-grid">
        <button v-for="theme in themes" :key="theme.key" class="theme-card" :class="{ active: form.themeKey === theme.key }" @tap="form.themeKey = theme.key">
          <text class="theme-name">{{ theme.name }}</text>
          <text class="theme-desc">{{ theme.description }}</text>
        </button>
      </view>
    </view>

    <view class="panel">
      <text class="panel-title">基础设置</text>
      <view class="field-row">
        <view class="field">
          <text class="field-label">人数</text>
          <input class="field-input" type="number" :value="form.servings" @input="form.servings = $event.detail.value" />
        </view>
        <view class="field">
          <text class="field-label">菜数</text>
          <input class="field-input" type="number" :value="form.targetCount" @input="form.targetCount = $event.detail.value" />
        </view>
      </view>
      <view class="field">
        <text class="field-label">餐次</text>
        <picker :range="mealTypes" range-key="label" :value="mealTypeIndex" @change="onMealTypeChange">
          <view class="picker-value">{{ mealTypes[mealTypeIndex].label }}</view>
        </picker>
      </view>
    </view>

    <view v-if="mode === 'custom'" class="panel">
      <text class="panel-title">偏好</text>
      <view class="field">
        <text class="field-label">已有食材</text>
        <input class="field-input" :value="ingredientsText" placeholder="例如：鸡蛋、番茄、豆腐" @input="ingredientsText = $event.detail.value" />
      </view>
      <view class="field">
        <text class="field-label">忌口</text>
        <input class="field-input" :value="avoidText" placeholder="例如：香菜、内脏" @input="avoidText = $event.detail.value" />
      </view>
      <view class="field">
        <text class="field-label">单菜最长耗时</text>
        <input class="field-input" type="number" :value="form.maxMinutes" placeholder="可选，分钟" @input="form.maxMinutes = $event.detail.value" />
      </view>
    </view>

    <button class="generate-button" :disabled="generating" @tap="generate">
      {{ generating ? '生成中...' : '生成配菜方案' }}
    </button>
    <text v-if="notice" class="notice">{{ notice }}</text>
  </view>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { generateMealPlan, getMealPlanThemes } from '../../services/meal-plan-api'

const modes = [
  { key: 'theme', label: '主题' },
  { key: 'custom', label: '自定义' },
  { key: 'random', label: '随机' }
]
const mealTypes = [
  { key: 'lunch', label: '午餐' },
  { key: 'dinner', label: '晚餐' },
  { key: 'all_day', label: '全天' },
  { key: 'breakfast', label: '早餐' }
]
const mode = ref('theme')
const themes = ref([])
const themesLoading = ref(false)
const generating = ref(false)
const notice = ref('')
const mealTypeIndex = ref(1)
const ingredientsText = ref('')
const avoidText = ref('')
const form = reactive({
  themeKey: 'balanced',
  servings: 2,
  targetCount: 4,
  mealType: 'dinner',
  maxMinutes: ''
})
const selectedMode = computed(() => (mode.value === 'theme' ? 'theme' : mode.value === 'custom' ? 'custom' : 'random'))

function splitText(value) {
  return String(value || '')
    .split(/[，,、\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function onMealTypeChange(event) {
  mealTypeIndex.value = Number(event.detail.value)
  form.mealType = mealTypes[mealTypeIndex.value].key
}

async function loadThemes() {
  themesLoading.value = true
  try {
    const data = await getMealPlanThemes()
    themes.value = data
    if (!form.themeKey && data[0]) form.themeKey = data[0].key
  } catch {
    themes.value = [
      { key: 'balanced', name: '营养均衡', description: '兼顾荤素和家常菜。' },
      { key: 'quick_dinner', name: '快手晚餐', description: '适合下班后快速开饭。' }
    ]
    notice.value = '主题接口暂时不可用，已使用默认主题。'
  } finally {
    themesLoading.value = false
  }
}

async function generate() {
  const servings = Math.max(1, Number(form.servings) || 2)
  const targetCount = Math.max(1, Math.min(Number(form.targetCount) || 4, 8))
  generating.value = true
  notice.value = ''
  try {
    const payload = {
      mode: selectedMode.value,
      servings,
      mealType: form.mealType,
      targetCount,
      themeKey: selectedMode.value === 'theme' ? form.themeKey : '',
      availableIngredients: splitText(ingredientsText.value),
      avoidKeywords: splitText(avoidText.value)
    }
    if (form.maxMinutes) payload.maxMinutes = Number(form.maxMinutes)
    const plan = await generateMealPlan(payload)
    uni.navigateTo({ url: `/pages/meal-plan/detail?id=${plan.id}` })
  } catch (cause) {
    notice.value = cause?.response?.detail || '方案生成失败，请稍后重试。'
  } finally {
    generating.value = false
  }
}

onMounted(loadThemes)
</script>

<style scoped>
.plan-page { min-height: 100vh; padding: 28rpx 28rpx calc(120rpx + env(safe-area-inset-bottom)); background: #f7f4ee; }
.hero { padding: 22rpx 0 28rpx; }
.eyebrow { display: block; color: #7b6f5d; font-size: 24rpx; font-weight: 800; }
.title { display: block; margin-top: 10rpx; color: #24221f; font-size: 52rpx; font-weight: 900; line-height: 1.12; }
.subtitle { display: block; margin-top: 16rpx; color: #676156; font-size: 27rpx; line-height: 1.55; }
.mode-tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12rpx; margin: 18rpx 0 22rpx; }
.mode-tab { height: 72rpx; border: 2rpx solid #d9cbb8; border-radius: 8rpx; color: #5f5649; font-size: 26rpx; font-weight: 800; }
.mode-tab.active { border-color: #254f47; background: #254f47; color: #fff; }
.panel { margin-top: 20rpx; padding: 26rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.panel-title { display: block; color: #25221d; font-size: 31rpx; font-weight: 900; }
.status { padding: 24rpx 0 0; color: #766e63; font-size: 25rpx; }
.theme-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 20rpx; }
.theme-card { min-height: 150rpx; padding: 20rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; text-align: left; }
.theme-card.active { border-color: #c55335; background: #fff4ec; }
.theme-name { display: block; color: #25221d; font-size: 27rpx; font-weight: 900; }
.theme-desc { display: block; margin-top: 10rpx; color: #756a5b; font-size: 23rpx; line-height: 1.35; }
.field-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.field { margin-top: 22rpx; }
.field-label { display: block; margin-bottom: 10rpx; color: #4d473f; font-size: 25rpx; font-weight: 800; }
.field-input, .picker-value { width: 100%; height: 82rpx; padding: 0 22rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; color: #25221d; font-size: 28rpx; line-height: 82rpx; }
.generate-button { height: 88rpx; margin-top: 28rpx; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 29rpx; font-weight: 900; }
.generate-button[disabled] { opacity: .55; }
.notice { display: block; margin-top: 18rpx; color: #b6492b; font-size: 24rpx; line-height: 1.45; }
</style>
