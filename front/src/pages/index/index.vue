<template>
  <view class="page">
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
import { computed, ref } from 'vue'
import { categoryTabs, recipes, skills, sourceProjects } from '../../utils/cookbook'

const keyword = ref('')
const activeCategory = ref('all')

const filteredRecipes = computed(() => {
  const query = keyword.value.trim().toLowerCase()

  return recipes.filter((recipe) => {
    const categoryMatched = activeCategory.value === 'all' || recipe.category === activeCategory.value
    const searchText = [
      recipe.title,
      recipe.summary,
      recipe.method,
      recipe.difficulty,
      recipe.source,
      ...recipe.tags,
      ...recipe.ingredients
    ]
      .join(' ')
      .toLowerCase()
    return categoryMatched && (!query || searchText.includes(query))
  })
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
  const pool = filteredRecipes.value.length > 0 ? filteredRecipes.value : recipes
  const recipe = pool[Math.floor(Math.random() * pool.length)]
  openRecipe(recipe.id)
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 28rpx 28rpx 56rpx;
  background: #f7f4ee;
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
