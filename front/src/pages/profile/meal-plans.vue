<template>
  <view class="list-page">
    <view class="page-head">
      <text class="page-title">我的配菜方案</text>
      <text class="page-subtitle">保存过的搭配会在这里留档。</text>
    </view>

    <view v-if="loading" class="status">正在加载...</view>
    <view v-else-if="items.length === 0" class="empty">还没有保存配菜方案</view>
    <view v-else class="plan-list">
      <view v-for="item in items" :key="item.id" class="plan-card">
        <button class="plan-main" @tap="openPlan(item.id)">
          <text class="plan-title">{{ item.title }}</text>
          <text class="plan-meta">{{ item.servings }} 人份 · {{ item.items.length }} 道菜 · {{ item.totalMinutes }} 分钟</text>
          <text class="plan-summary">{{ item.summary }}</text>
        </button>
        <button class="delete-button" @tap="remove(item.id)">删除</button>
      </view>
    </view>

    <button v-if="hasMore" class="load-more" :disabled="loadingMore" @tap="loadMore">{{ loadingMore ? '加载中...' : '加载更多' }}</button>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { deleteMealPlan } from '../../services/meal-plan-api'
import { getMyMealPlans } from '../../services/profile-api'
import { getAccessToken } from '../../services/auth-storage'

const items = ref([])
const page = ref(1)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)

function ensureLogin() {
  if (getAccessToken()) return true
  uni.redirectTo({ url: '/pages/auth/login?next=%2Fpages%2Fprofile%2Fmeal-plans' })
  return false
}

async function load(append = false) {
  if (!ensureLogin()) return
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const nextPage = append ? page.value + 1 : 1
    const data = await getMyMealPlans(nextPage)
    const results = data.results || data
    items.value = append ? [...items.value, ...results] : results
    page.value = nextPage
    hasMore.value = Boolean(data.next)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  if (hasMore.value && !loadingMore.value) load(true)
}

function openPlan(id) {
  uni.navigateTo({ url: `/pages/meal-plan/detail?id=${id}` })
}

function remove(id) {
  uni.showModal({
    title: '删除方案',
    content: '删除后不会再出现在我的列表中。',
    success: async (result) => {
      if (!result.confirm) return
      try {
        await deleteMealPlan(id)
        items.value = items.value.filter((item) => item.id !== id)
      } catch {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  })
}

onShow(() => load(false))
</script>

<style scoped>
.list-page { min-height: 100vh; padding: 28rpx; background: #f7f4ee; }
.page-head { padding: 18rpx 0 26rpx; }
.page-title { display: block; color: #25221d; font-size: 40rpx; font-weight: 900; }
.page-subtitle { display: block; margin-top: 10rpx; color: #766e63; font-size: 25rpx; }
.status, .empty { padding: 70rpx 0; color: #766e63; font-size: 26rpx; text-align: center; }
.plan-list { display: flex; flex-direction: column; gap: 18rpx; }
.plan-card { display: flex; gap: 14rpx; padding: 22rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.plan-main { flex: 1; min-width: 0; text-align: left; }
.plan-title { display: block; color: #25221d; font-size: 29rpx; font-weight: 900; }
.plan-meta { display: block; margin-top: 10rpx; color: #c55335; font-size: 23rpx; font-weight: 800; }
.plan-summary { display: block; margin-top: 10rpx; color: #6b6255; font-size: 24rpx; line-height: 1.45; }
.delete-button { align-self: center; width: 96rpx; height: 58rpx; color: #b6492b; font-size: 23rpx; }
.load-more { width: 240rpx; height: 70rpx; margin: 28rpx auto 0; border: 2rpx solid #d9cbb8; border-radius: 8rpx; color: #254f47; font-size: 25rpx; }
</style>
