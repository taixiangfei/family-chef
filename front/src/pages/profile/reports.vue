<template>
  <view class="list-page">
    <view class="page-head">
      <text class="page-title">我的举报</text>
      <text class="page-subtitle">查看已提交举报的处理状态。</text>
    </view>

    <view v-if="loading" class="status">正在加载...</view>
    <view v-else-if="items.length === 0" class="empty">还没有提交过举报</view>
    <view v-else class="item-list">
      <view v-for="item in items" :key="item.id" class="record-card">
        <view class="record-topline">
          <text class="record-title">{{ item.target_title || targetText(item.target_type) }}</text>
          <text class="status-tag">{{ statusText(item.status) }}</text>
        </view>
        <text class="record-content">{{ item.reason }}</text>
        <text v-if="item.resolution" class="record-resolution">{{ item.resolution }}</text>
        <text class="record-time">{{ formatDate(item.created_at) }}</text>
      </view>
    </view>

    <button v-if="hasMore" class="load-more" :disabled="loadingMore" @tap="loadMore">{{ loadingMore ? '加载中...' : '加载更多' }}</button>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { getAccessToken } from '../../services/auth-storage'
import { getMyReports } from '../../services/profile-api'

const items = ref([])
const page = ref(1)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const labels = { pending: '待处理', resolved: '已处理', dismissed: '已驳回' }

function ensureLogin() {
  if (getAccessToken()) return true
  uni.redirectTo({ url: '/pages/auth/login?next=%2Fpages%2Fprofile%2Freports' })
  return false
}

async function load(append = false) {
  if (!ensureLogin()) return
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const nextPage = append ? page.value + 1 : 1
    const data = await getMyReports(nextPage)
    const results = data.results || data
    items.value = append ? [...items.value, ...results] : results
    page.value = nextPage
    hasMore.value = Boolean(data.next)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function targetText(value) {
  return value === 'comment' ? '评论' : '菜品'
}

function statusText(value) {
  return labels[value] || value
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN') : ''
}

function loadMore() {
  if (hasMore.value && !loadingMore.value) load(true)
}

onShow(() => load(false))
</script>

<style scoped>
.list-page { min-height: 100vh; padding: 28rpx; background: #f7f4ee; }
.page-head { padding: 18rpx 0 26rpx; }
.page-title { display: block; color: #25221d; font-size: 40rpx; font-weight: 900; }
.page-subtitle { display: block; margin-top: 10rpx; color: #766e63; font-size: 25rpx; }
.status, .empty { padding: 70rpx 0; color: #766e63; font-size: 26rpx; text-align: center; }
.item-list { display: flex; flex-direction: column; gap: 18rpx; }
.record-card { padding: 24rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.record-topline { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
.record-title { min-width: 0; color: #25221d; font-size: 28rpx; font-weight: 900; }
.status-tag { flex: 0 0 auto; padding: 6rpx 12rpx; border-radius: 6rpx; background: #e8f0dc; color: #405835; font-size: 22rpx; }
.record-content { display: block; margin-top: 14rpx; color: #4e473e; font-size: 26rpx; line-height: 1.5; }
.record-resolution { display: block; margin-top: 12rpx; color: #8b6a49; font-size: 24rpx; line-height: 1.45; }
.record-time { display: block; margin-top: 12rpx; color: #8a7e6d; font-size: 22rpx; }
.load-more { width: 240rpx; height: 70rpx; margin: 28rpx auto 0; border: 2rpx solid #d9cbb8; border-radius: 8rpx; color: #254f47; font-size: 25rpx; }
</style>
