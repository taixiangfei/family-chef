<template>
  <view class="page">
    <view class="account-bar">
      <button class="account-button" @tap="openAccount">{{ accountLabel }}</button>
    </view>
    <view class="hero">
      <view class="hero-copy">
        <text class="eyebrow">Family Chef</text>
        <text class="title">家常主厨</text>
        <text class="subtitle">把开源菜谱整理成适合手机边看边做的教程。</text>
      </view>
      <image class="hero-image" src="/static/images/tomato-egg.png" mode="aspectFill" />
    </view>

    <view class="search-row">
      <input
        class="search-input"
        :value="keyword"
        placeholder="搜索菜名、食材、做法"
        placeholder-class="search-placeholder"
        confirm-type="search"
        @input="onSearchInput"
      />
      <button class="random-button" @tap="openRandom">随机</button>
    </view>

    <scroll-view class="tabs" scroll-x enable-flex>
      <button
        v-for="tab in categoryTabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeCategory === tab.key }"
        @tap="activeCategory = tab.key"
      >
        {{ tab.label }}
      </button>
    </scroll-view>

    <view v-if="loading" class="data-status">正在加载最新菜谱...</view>
    <view v-else-if="notice" class="data-status">{{ notice }}</view>

    <view class="section-head">
      <text class="section-title">今日可做</text>
      <text class="section-meta">{{ filteredRecipes.length }} 个教程</text>
    </view>

    <view class="recipe-grid">
      <button v-for="recipe in filteredRecipes" :key="recipe.id" class="recipe-card" @tap="openRecipe(recipe.id)">
        <image class="recipe-image" :src="recipe.image" mode="aspectFill" />
        <view class="recipe-body">
          <view class="recipe-topline">
            <text class="recipe-title">{{ recipe.title }}</text>
            <text class="recipe-time">{{ recipe.time }} 分钟</text>
          </view>
          <text class="recipe-summary">{{ recipe.summary }}</text>
          <view class="recipe-tags">
            <text class="tag">{{ recipe.difficulty }}</text>
            <text class="tag">{{ recipe.method }}</text>
            <text class="tag">{{ recipe.source }}</text>
          </view>
        </view>
      </button>
    </view>

    <view class="empty" v-if="filteredRecipes.length === 0">
      <text class="empty-title">暂时没找到</text>
      <text class="empty-text">换个菜名、食材或做法试试。</text>
    </view>

    <button v-if="apiMode && hasMore" class="load-more" :disabled="loadingMore" @tap="loadMore">
      {{ loadingMore ? '正在加载...' : '加载更多' }}
    </button>

    <view class="knowledge">
      <view class="section-head compact">
        <text class="section-title">做菜基础</text>
        <text class="section-meta">来自开源项目的知识结构整理</text>
      </view>
      <view class="skill-list">
        <view v-for="skill in skills" :key="skill.title" class="skill-card">
          <text class="skill-title">{{ skill.title }}</text>
          <text class="skill-subtitle">{{ skill.subtitle }}</text>
          <view class="skill-points">
            <text v-for="point in skill.points" :key="point" class="skill-point">{{ point }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="sources">
      <text class="sources-title">参考来源</text>
      <view v-for="source in sourceProjects" :key="source.name" class="source-row">
        <text class="source-name">{{ source.name }}</text>
        <text class="source-note">{{ source.note }}</text>
        <text class="source-url">{{ source.url }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { categoryTabs as staticCategoryTabs, recipes as staticRecipes, skills, sourceProjects } from '../../utils/cookbook'
import { getCategories, getDishes } from '../../services/recipe-api'
import { filterStaticRecipes, mapCategories, mapDishToRecipe } from '../../services/recipe-adapter'
import { getAccessToken, getCurrentUser } from '../../services/auth-storage'

const keyword = ref('')
const activeCategory = ref('all')
const recipes = ref(staticRecipes)
const categoryTabs = ref(staticCategoryTabs)
const loading = ref(false)
const loadingMore = ref(false)
const notice = ref('')
const apiMode = ref(false)
const hasMore = ref(false)
const currentPage = ref(1)
const currentUser = ref(getCurrentUser())
let requestSequence = 0
let searchTimer

const accountLabel = computed(() => currentUser.value?.nickname || currentUser.value?.username || '登录')

const filteredRecipes = computed(() => {
  return apiMode.value
    ? recipes.value
    : filterStaticRecipes(staticRecipes, keyword.value, activeCategory.value)
})

function onSearchInput(event) {
  keyword.value = event.detail.value
}

function openRecipe(id) {
  uni.navigateTo({
    url: `/pages/recipe/detail?id=${id}`
  })
}

function openRandom() {
  const pool = filteredRecipes.value.length > 0 ? filteredRecipes.value : staticRecipes
  const recipe = pool[Math.floor(Math.random() * pool.length)]
  openRecipe(recipe.id)
}

function openAccount() {
  uni.navigateTo({
    url: getAccessToken() ? '/pages/profile/index' : '/pages/auth/login'
  })
}

async function loadCategories() {
  try {
    const categories = await getCategories()
    if (Array.isArray(categories) && categories.length) {
      categoryTabs.value = mapCategories(categories)
    }
  } catch {
    // Static category tabs remain available when the API is offline.
  }
}

async function loadDishes({ append = false } = {}) {
  const sequence = ++requestSequence
  const page = append ? currentPage.value + 1 : 1
  if (append) loadingMore.value = true
  else loading.value = true

  try {
    const data = await getDishes({
      search: keyword.value.trim(),
      category: activeCategory.value === 'all' ? '' : activeCategory.value,
      page,
      pageSize: 100
    })
    if (sequence !== requestSequence) return
    const items = (data.results || data).map(mapDishToRecipe)
    recipes.value = append ? [...recipes.value, ...items] : items
    currentPage.value = page
    hasMore.value = Boolean(data.next)
    apiMode.value = true
    notice.value = ''
  } catch {
    if (sequence !== requestSequence) return
    if (!append) {
      recipes.value = staticRecipes
      apiMode.value = false
      hasMore.value = false
      notice.value = '在线菜谱暂时不可用，当前使用本地菜谱。'
    } else {
      notice.value = '加载更多失败，请稍后重试。'
    }
  } finally {
    if (sequence === requestSequence) {
      loading.value = false
      loadingMore.value = false
    }
  }
}

function loadMore() {
  if (!loadingMore.value && hasMore.value) loadDishes({ append: true })
}

function scheduleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadDishes(), 300)
}

watch([keyword, activeCategory], scheduleSearch)
onMounted(() => {
  loadCategories()
  loadDishes()
})
onShow(() => {
  currentUser.value = getCurrentUser()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 28rpx 28rpx 56rpx;
  background: #f7f4ee;
}

.account-bar {
  display: flex;
  justify-content: flex-end;
  min-height: 52rpx;
}

.account-button {
  min-width: 104rpx;
  height: 52rpx;
  padding: 0 18rpx;
  border: 2rpx solid #d8ccb9;
  border-radius: 8rpx;
  color: #254f47;
  font-size: 23rpx;
  font-weight: 700;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  min-height: 260rpx;
  padding: 16rpx 0 28rpx;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.eyebrow {
  display: block;
  margin-bottom: 10rpx;
  color: #7b6f5d;
  font-size: 24rpx;
  font-weight: 700;
}

.title {
  display: block;
  color: #24221f;
  font-size: 56rpx;
  font-weight: 800;
  line-height: 1.1;
}

.subtitle {
  display: block;
  max-width: 430rpx;
  margin-top: 18rpx;
  color: #676156;
  font-size: 28rpx;
  line-height: 1.55;
}

.hero-image {
  width: 220rpx;
  height: 170rpx;
  border-radius: 8rpx;
  background: #fffaf2;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 8rpx;
}

.search-input {
  flex: 1;
  height: 84rpx;
  padding: 0 28rpx;
  border: 2rpx solid #e1d6c5;
  border-radius: 8rpx;
  background: #fffaf2;
  color: #25221d;
  font-size: 28rpx;
}

.search-placeholder {
  color: #a59b8d;
}

.random-button {
  width: 132rpx;
  height: 84rpx;
  line-height: 84rpx;
  border-radius: 8rpx;
  background: #254f47;
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
}

.tabs {
  display: flex;
  width: 100%;
  margin-top: 24rpx;
  white-space: nowrap;
}

.tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 108rpx;
  height: 64rpx;
  margin-right: 14rpx;
  padding: 0 24rpx;
  border: 2rpx solid #ded2bf;
  border-radius: 8rpx;
  color: #5f5649;
  font-size: 26rpx;
}

.tab.active {
  border-color: #c55335;
  background: #c55335;
  color: #fff;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20rpx;
  margin: 38rpx 0 20rpx;
}

.section-head.compact {
  margin-top: 0;
}

.section-title {
  color: #24221f;
  font-size: 34rpx;
  font-weight: 800;
}

.section-meta {
  color: #807665;
  font-size: 24rpx;
  text-align: right;
}

.data-status {
  margin-top: 16rpx;
  color: #8b7d6a;
  font-size: 23rpx;
  line-height: 1.4;
}

.recipe-grid {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.recipe-card {
  display: flex;
  width: 100%;
  min-height: 208rpx;
  overflow: hidden;
  border: 2rpx solid #eadfcd;
  border-radius: 8rpx;
  background: #fffaf2;
  text-align: left;
}

.recipe-image {
  flex: 0 0 208rpx;
  width: 208rpx;
  height: 208rpx;
  background: #eee4d5;
}

.recipe-body {
  flex: 1;
  min-width: 0;
  padding: 22rpx;
}

.recipe-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.recipe-title {
  min-width: 0;
  color: #24221f;
  font-size: 32rpx;
  font-weight: 800;
}

.recipe-time {
  flex: 0 0 auto;
  color: #c55335;
  font-size: 24rpx;
  font-weight: 700;
}

.recipe-summary {
  display: block;
  margin-top: 12rpx;
  color: #6b6255;
  font-size: 25rpx;
  line-height: 1.45;
}

.recipe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 18rpx;
}

.tag {
  padding: 8rpx 14rpx;
  border-radius: 6rpx;
  background: #efe6d7;
  color: #5d5142;
  font-size: 22rpx;
}

.empty {
  padding: 60rpx 20rpx;
  text-align: center;
}

.empty-title,
.empty-text {
  display: block;
}

.empty-title {
  color: #25221d;
  font-size: 32rpx;
  font-weight: 800;
}

.empty-text {
  margin-top: 12rpx;
  color: #766e63;
  font-size: 26rpx;
}

.load-more {
  width: 260rpx;
  height: 72rpx;
  margin: 28rpx auto 0;
  border: 2rpx solid #d9cbb8;
  border-radius: 8rpx;
  color: #254f47;
  font-size: 25rpx;
}

.knowledge {
  margin-top: 44rpx;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.skill-card {
  padding: 24rpx;
  border: 2rpx solid #eadfcd;
  border-radius: 8rpx;
  background: #fffaf2;
}

.skill-title {
  display: block;
  color: #25221d;
  font-size: 30rpx;
  font-weight: 800;
}

.skill-subtitle {
  display: block;
  margin-top: 8rpx;
  color: #7a6f60;
  font-size: 25rpx;
}

.skill-points {
  margin-top: 18rpx;
}

.skill-point {
  display: block;
  margin-top: 10rpx;
  color: #4d473f;
  font-size: 25rpx;
  line-height: 1.45;
}

.sources {
  margin-top: 40rpx;
  padding-top: 28rpx;
  border-top: 2rpx solid #e5dac8;
}

.sources-title {
  display: block;
  color: #25221d;
  font-size: 28rpx;
  font-weight: 800;
}

.source-row {
  margin-top: 18rpx;
}

.source-name,
.source-note,
.source-url {
  display: block;
}

.source-name {
  color: #254f47;
  font-size: 26rpx;
  font-weight: 800;
}

.source-note,
.source-url {
  margin-top: 6rpx;
  color: #766e63;
  font-size: 23rpx;
  line-height: 1.45;
}

.source-url {
  color: #9b4a32;
}

@media screen and (min-width: 768px) {
  .page {
    max-width: 980px;
    margin: 0 auto;
    padding: 36px 32px 72px;
  }

  .recipe-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-image {
    width: 280rpx;
    height: 210rpx;
  }
}
</style>
