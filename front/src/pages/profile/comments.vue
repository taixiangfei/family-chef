<template>
  <view class="list-page">
    <view class="page-head">
      <text class="page-title">我的评论</text>
      <text class="page-subtitle">这里能看到你留在菜谱下的厨房留言。</text>
    </view>

    <view v-if="loading" class="status">正在加载...</view>
    <view v-else-if="items.length === 0" class="empty">还没有发表过评论</view>
    <view v-else class="item-list">
      <view v-for="item in items" :key="item.id" class="record-card">
        <view class="record-topline">
          <text class="record-title">{{ item.dish_name || '菜品' }}</text>
          <text class="status-tag">{{ statusText(item.status) }}</text>
        </view>
        <text class="record-content">{{ item.content }}</text>
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
import { getMyComments } from '../../services/profile-api'

const items = ref([])
const page = ref(1)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const labels = { pending: '待审核', visible: '可见', hidden: '已隐藏', rejected: '已拒绝', deleted: '已删除' }

function ensureLogin() {
  if (getAccessToken()) return true
  uni.redirectTo({ url: '/pages/auth/login?next=%2Fpages%2Fprofile%2Fcomments' })
  return false
}

async function load(append = false) {
  if (!ensureLogin()) return
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const nextPage = append ? page.value + 1 : 1
    const data = await getMyComments(nextPage)
    const results = data.results || data
    items.value = append ? [...items.value, ...results] : results
    page.value = nextPage
    hasMore.value = Boolean(data.next)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
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
.list-page { min-height: 100vh; padding: 28rpx; background: linear-gradient(180deg, #f4ead8 0%, #fff7ea 100%); }
.page-head { margin-bottom: 24rpx; padding: 26rpx 28rpx; border: 2rpx solid #d7b485; border-radius: 8rpx; background: #f9e4c2; }
.page-title { display: block; color: #2b241c; font-size: 40rpx; font-weight: 900; }
.page-subtitle { display: block; margin-top: 10rpx; color: #6a4d39; font-size: 25rpx; line-height: 1.45; }
.status, .empty { padding: 70rpx 0; color: #7b604f; font-size: 26rpx; text-align: center; }
.item-list { display: flex; flex-direction: column; gap: 18rpx; }
.record-card { padding: 24rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; box-shadow: 0 6rpx 0 #ead4b4; }
.record-topline { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
.record-title { min-width: 0; color: #2b241c; font-size: 28rpx; font-weight: 900; }
.status-tag { flex: 0 0 auto; padding: 7rpx 13rpx; border-radius: 6rpx; background: #edf1dd; color: #3e5d36; font-size: 22rpx; font-weight: 900; }
.record-content { display: block; margin-top: 14rpx; color: #4f3a2b; font-size: 26rpx; line-height: 1.5; }
.record-time { display: block; margin-top: 12rpx; color: #8a6049; font-size: 22rpx; }
.load-more { width: 240rpx; height: 72rpx; margin: 30rpx auto 0; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; color: #1f5c4c; font-size: 25rpx; font-weight: 900; }
</style>
