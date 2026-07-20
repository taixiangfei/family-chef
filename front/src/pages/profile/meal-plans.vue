<template>
  <view class="list-page">
    <view class="page-head">
      <text class="page-title">我的配菜方案</text>
      <text class="page-subtitle">保存过的搭配会在这里留进菜单夹。</text>
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
.list-page { min-height: 100vh; padding: 28rpx; background: linear-gradient(180deg, #f4ead8 0%, #fff7ea 100%); }
.page-head { margin-bottom: 24rpx; padding: 26rpx 28rpx; border: 2rpx solid #d7b485; border-radius: 8rpx; background: #f9e4c2; }
.page-title { display: block; color: #2b241c; font-size: 40rpx; font-weight: 900; }
.page-subtitle { display: block; margin-top: 10rpx; color: #6a4d39; font-size: 25rpx; line-height: 1.45; }
.status, .empty { padding: 70rpx 0; color: #7b604f; font-size: 26rpx; text-align: center; }
.plan-list { display: flex; flex-direction: column; gap: 18rpx; }
.plan-card { display: flex; gap: 14rpx; padding: 22rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; box-shadow: 0 6rpx 0 #ead4b4; }
.plan-main { flex: 1; min-width: 0; text-align: left; }
.plan-title { display: block; color: #2b241c; font-size: 29rpx; font-weight: 900; }
.plan-meta { display: block; margin-top: 10rpx; color: #c84f31; font-size: 23rpx; font-weight: 900; }
.plan-summary { display: block; margin-top: 10rpx; color: #6a4d39; font-size: 24rpx; line-height: 1.45; }
.delete-button { align-self: center; width: 96rpx; height: 58rpx; color: #a44d32; font-size: 23rpx; font-weight: 900; }
.load-more { width: 240rpx; height: 72rpx; margin: 30rpx auto 0; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; color: #1f5c4c; font-size: 25rpx; font-weight: 900; }
</style>
