<template>
  <view class="page">
    <view class="account-bar">
      <text class="kitchen-mark">灶台已预热</text>
      <button class="account-button" @tap="openAccount">{{ accountLabel }}</button>
    </view>
    <view class="hero">
      <view class="hero-copy">
        <text class="eyebrow">Family Chef Kitchen</text>
        <text class="title">家常主厨</text>
        <text class="subtitle">像翻厨房菜谱夹一样，找一道今天真能端上桌的家常菜。</text>
        <view class="hero-chips">
          <text class="hero-chip">快手</text>
          <text class="hero-chip">下饭</text>
          <text class="hero-chip">家里有啥做啥</text>
        </view>
      </view>
      <view class="hero-plate">
        <image class="hero-image" src="/static/images/tomato-egg.png" mode="aspectFill" />
        <text class="plate-label">今日锅气</text>
      </view>
    </view>

    <view class="search-row">
      <input
        class="search-input"
        :value="keyword"
        placeholder="搜菜名、食材、做法"
        placeholder-class="search-placeholder"
        confirm-type="search"
        @input="onSearchInput"
      />
      <button class="random-button" @tap="openRandom">开盲锅</button>
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
      <text class="section-title">今日灶台</text>
      <text class="section-meta">{{ filteredRecipes.length }} 个教程</text>
    </view>

    <view class="recipe-grid">
      <button v-for="recipe in filteredRecipes" :key="recipe.id" class="recipe-card" @tap="openRecipe(recipe.id)">
        <image class="recipe-image" :src="recipe.image" mode="aspectFill" />
        <view class="recipe-body">
          <view class="recipe-topline">
            <text class="recipe-title">{{ recipe.title }}</text>
            <text class="recipe-time">{{ recipe.time }} 分钟出锅</text>
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
        <text class="empty-title">这口锅还没翻到</text>
        <text class="empty-text">换个菜名、食材或做法试试。</text>
    </view>

    <button v-if="apiMode && hasMore" class="load-more" :disabled="loadingMore" @tap="loadMore">
      {{ loadingMore ? '正在加载...' : '加载更多' }}
    </button>

    <view class="knowledge">
      <view class="section-head compact">
        <text class="section-title">厨房基本功</text>
        <text class="section-meta">切配、火候、调味</text>
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
  if (getAccessToken()) {
    uni.switchTab({ url: '/pages/profile/index' })
    return
  }
  uni.navigateTo({ url: '/pages/auth/login?next=%2Fpages%2Fprofile%2Findex' })
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
  padding: 28rpx 28rpx calc(124rpx + env(safe-area-inset-bottom));
  background:
    linear-gradient(180deg, #f4ead8 0%, #fff7ea 34%, #f6ead5 100%);
}

.account-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 58rpx;
}

.kitchen-mark {
  color: #8a6049;
  font-size: 23rpx;
  font-weight: 800;
}

.account-button {
  min-width: 116rpx;
  height: 56rpx;
  padding: 0 20rpx;
  border: 2rpx solid #d8b98f;
  border-radius: 28rpx;
  background: #fff7ea;
  color: #1f5c4c;
  font-size: 23rpx;
  font-weight: 900;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  min-height: 320rpx;
  margin-top: 18rpx;
  padding: 28rpx;
  border: 2rpx solid #d7b485;
  border-radius: 8rpx;
  background:
    linear-gradient(135deg, #fff7ea 0%, #f8dfbd 100%);
  box-shadow: 0 10rpx 0 #e2c79f;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.eyebrow {
  display: block;
  margin-bottom: 10rpx;
  color: #a44d32;
  font-size: 23rpx;
  font-weight: 900;
  letter-spacing: 0;
}

.title {
  display: block;
  color: #2b241c;
  font-size: 60rpx;
  font-weight: 900;
  line-height: 1.08;
}

.subtitle {
  display: block;
  max-width: 440rpx;
  margin-top: 18rpx;
  color: #6e533d;
  font-size: 28rpx;
  line-height: 1.55;
}

.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 22rpx;
}

.hero-chip {
  padding: 8rpx 14rpx;
  border: 2rpx solid #dfc49b;
  border-radius: 24rpx;
  background: #fffaf1;
  color: #6f4a32;
  font-size: 21rpx;
  font-weight: 800;
}

.hero-plate {
  flex: 0 0 220rpx;
  width: 220rpx;
  padding: 14rpx;
  border: 3rpx solid #fffaf1;
  border-radius: 50%;
  background: #eaf0df;
  box-shadow: inset 0 0 0 10rpx #fffaf1;
}

.hero-image {
  width: 192rpx;
  height: 192rpx;
  border-radius: 50%;
  background: #e9d4b9;
}

.plate-label {
  display: block;
  margin-top: 10rpx;
  color: #1f5c4c;
  font-size: 21rpx;
  font-weight: 900;
  text-align: center;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-top: 34rpx;
}

.search-input {
  flex: 1;
  height: 88rpx;
  padding: 0 28rpx;
  border: 2rpx solid #d8b98f;
  border-radius: 8rpx;
  background: #fffaf1;
  color: #2b241c;
  font-size: 28rpx;
}

.search-placeholder {
  color: #a98869;
}

.random-button {
  width: 150rpx;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 8rpx;
  background: #c84f31;
  color: #fffaf1;
  font-size: 26rpx;
  font-weight: 900;
  box-shadow: 0 6rpx 0 #91361f;
}

.tabs {
  display: flex;
  width: 100%;
  margin-top: 28rpx;
  white-space: nowrap;
}

.tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 112rpx;
  height: 66rpx;
  margin-right: 14rpx;
  padding: 0 24rpx;
  border: 2rpx solid #d9bc91;
  border-radius: 33rpx;
  background: #fff7ea;
  color: #6f4a32;
  font-size: 25rpx;
  font-weight: 800;
}

.tab.active {
  border-color: #1f5c4c;
  background: #1f5c4c;
  color: #fffaf1;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20rpx;
  margin: 42rpx 0 20rpx;
}

.section-head.compact {
  margin-top: 0;
}

.section-title {
  color: #2b241c;
  font-size: 34rpx;
  font-weight: 900;
}

.section-meta {
  color: #8a6049;
  font-size: 24rpx;
  text-align: right;
}

.data-status {
  display: block;
  margin-top: 18rpx;
  padding: 16rpx 18rpx;
  border-left: 8rpx solid #d8b98f;
  background: #fff3df;
  color: #7b604f;
  font-size: 23rpx;
  line-height: 1.4;
}

.recipe-grid {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.recipe-card {
  display: flex;
  width: 100%;
  min-height: 214rpx;
  overflow: hidden;
  border: 2rpx solid #d8b98f;
  border-radius: 8rpx;
  background: #fffaf1;
  box-shadow: 0 8rpx 0 #ead4b4;
  text-align: left;
}

.recipe-image {
  flex: 0 0 214rpx;
  width: 214rpx;
  height: 214rpx;
  background: #ead8bd;
}

.recipe-body {
  flex: 1;
  min-width: 0;
  padding: 22rpx 22rpx 20rpx;
}

.recipe-topline {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14rpx;
}

.recipe-title {
  min-width: 0;
  color: #2b241c;
  font-size: 31rpx;
  font-weight: 900;
  line-height: 1.28;
}

.recipe-time {
  flex: 0 0 auto;
  max-width: 132rpx;
  color: #c84f31;
  font-size: 22rpx;
  font-weight: 900;
  line-height: 1.25;
  text-align: right;
}

.recipe-summary {
  display: block;
  margin-top: 12rpx;
  color: #6a4d39;
  font-size: 25rpx;
  line-height: 1.45;
}

.recipe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 16rpx;
}

.tag {
  padding: 8rpx 14rpx;
  border-radius: 6rpx;
  background: #edf1dd;
  color: #3e5d36;
  font-size: 22rpx;
  font-weight: 800;
}

.empty {
  padding: 68rpx 20rpx;
  text-align: center;
}

.empty-title,
.empty-text {
  display: block;
}

.empty-title {
  color: #2b241c;
  font-size: 32rpx;
  font-weight: 900;
}

.empty-text {
  margin-top: 12rpx;
  color: #7b604f;
  font-size: 26rpx;
}

.load-more {
  width: 270rpx;
  height: 74rpx;
  margin: 32rpx auto 0;
  border: 2rpx solid #d8b98f;
  border-radius: 8rpx;
  background: #fff7ea;
  color: #1f5c4c;
  font-size: 25rpx;
  font-weight: 800;
}

.knowledge {
  margin-top: 52rpx;
  padding: 28rpx;
  border: 2rpx dashed #c69d6c;
  border-radius: 8rpx;
  background: #f9e4c2;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.skill-card {
  padding: 24rpx;
  border-left: 10rpx solid #1f5c4c;
  border-radius: 8rpx;
  background: #fffaf1;
}

.skill-title {
  display: block;
  color: #2b241c;
  font-size: 30rpx;
  font-weight: 900;
}

.skill-subtitle {
  display: block;
  margin-top: 8rpx;
  color: #8a6049;
  font-size: 25rpx;
}

.skill-points {
  margin-top: 18rpx;
}

.skill-point {
  display: block;
  margin-top: 10rpx;
  color: #4f3a2b;
  font-size: 25rpx;
  line-height: 1.45;
}

.sources {
  margin-top: 40rpx;
  padding: 26rpx 0 0;
  border-top: 2rpx solid #d8b98f;
}

.sources-title {
  display: block;
  color: #2b241c;
  font-size: 28rpx;
  font-weight: 900;
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
  color: #1f5c4c;
  font-size: 26rpx;
  font-weight: 900;
}

.source-note,
.source-url {
  margin-top: 6rpx;
  color: #7b604f;
  font-size: 23rpx;
  line-height: 1.45;
}

.source-url {
  color: #a44d32;
}

@media screen and (min-width: 768px) {
  .page {
    max-width: 980px;
    margin: 0 auto;
    padding: 36px 32px 76px;
  }

  .recipe-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-plate {
    flex-basis: 260rpx;
    width: 260rpx;
  }

  .hero-image {
    width: 232rpx;
    height: 232rpx;
  }
}
</style>
