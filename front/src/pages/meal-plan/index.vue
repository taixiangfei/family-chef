<template>
  <view class="plan-page">
    <view class="hero">
      <text class="eyebrow">Kitchen Board</text>
      <text class="title">今天这样搭</text>
      <text class="subtitle">把已有菜谱像备菜一样排开，搭出一桌有主菜、有青菜、有汤气的家常菜单。</text>
    </view>

    <view class="mode-tabs">
      <button v-for="item in modes" :key="item.key" class="mode-tab" :class="{ active: mode === item.key }" @tap="mode = item.key">
        {{ item.label }}
      </button>
    </view>

    <view v-if="mode === 'theme'" class="panel">
      <text class="panel-title">今晚餐桌主题</text>
      <view v-if="themesLoading" class="status">正在加载主题...</view>
      <view v-else class="theme-grid">
        <button v-for="theme in themes" :key="theme.key" class="theme-card" :class="{ active: form.themeKey === theme.key }" @tap="form.themeKey = theme.key">
          <text class="theme-name">{{ theme.name }}</text>
          <text class="theme-desc">{{ theme.description }}</text>
        </button>
      </view>
    </view>

    <view class="panel">
      <text class="panel-title">备菜设置</text>
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
      <text class="panel-title">冰箱与忌口</text>
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
      {{ generating ? '正在配菜...' : '排一桌菜单' }}
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
.plan-page { min-height: 100vh; padding: 28rpx 28rpx calc(124rpx + env(safe-area-inset-bottom)); background: linear-gradient(180deg, #f4ead8 0%, #fff7ea 42%, #f6ead5 100%); }
.hero { padding: 30rpx 28rpx; border: 2rpx solid #d7b485; border-radius: 8rpx; background: #f9e4c2; box-shadow: 0 8rpx 0 #e2c79f; }
.eyebrow { display: block; color: #a44d32; font-size: 24rpx; font-weight: 900; }
.title { display: block; margin-top: 10rpx; color: #2b241c; font-size: 54rpx; font-weight: 900; line-height: 1.12; }
.subtitle { display: block; margin-top: 16rpx; color: #6a4d39; font-size: 27rpx; line-height: 1.55; }
.mode-tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12rpx; margin: 30rpx 0 22rpx; }
.mode-tab { height: 74rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; color: #6f4a32; font-size: 26rpx; font-weight: 900; }
.mode-tab.active { border-color: #1f5c4c; background: #1f5c4c; color: #fffaf1; }
.panel { margin-top: 22rpx; padding: 28rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; }
.panel-title { display: block; color: #2b241c; font-size: 31rpx; font-weight: 900; }
.status { padding: 24rpx 0 0; color: #7b604f; font-size: 25rpx; }
.theme-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 22rpx; }
.theme-card { min-height: 158rpx; padding: 20rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fff7ea; text-align: left; }
.theme-card.active { border-color: #c84f31; background: #fff0df; box-shadow: inset 0 0 0 4rpx #ffd9c8; }
.theme-name { display: block; color: #2b241c; font-size: 27rpx; font-weight: 900; }
.theme-desc { display: block; margin-top: 10rpx; color: #7b604f; font-size: 23rpx; line-height: 1.35; }
.field-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.field { margin-top: 22rpx; }
.field-label { display: block; margin-bottom: 10rpx; color: #4f3a2b; font-size: 25rpx; font-weight: 900; }
.field-input, .picker-value { width: 100%; height: 84rpx; padding: 0 22rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fff7ea; color: #2b241c; font-size: 28rpx; line-height: 84rpx; }
.generate-button { height: 90rpx; margin-top: 30rpx; border-radius: 8rpx; background: #c84f31; color: #fffaf1; font-size: 29rpx; font-weight: 900; box-shadow: 0 7rpx 0 #91361f; }
.generate-button[disabled] { opacity: .55; }
.notice { display: block; margin-top: 20rpx; padding: 14rpx 16rpx; border-left: 8rpx solid #c84f31; background: #fff0df; color: #a44d32; font-size: 24rpx; line-height: 1.45; }
</style>
