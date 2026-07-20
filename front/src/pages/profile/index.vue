<template>
  <view class="profile-page">
    <view class="profile-hero">
      <view class="avatar">{{ initial }}</view>
      <view class="profile-copy">
        <text class="profile-title">{{ loggedIn ? displayName : '我的' }}</text>
        <text class="profile-subtitle">{{ loggedIn ? '管理资料和个人记录' : '登录后保存配菜方案、查看评论和举报' }}</text>
      </view>
    </view>

    <view v-if="!loggedIn" class="guest-panel">
      <button class="primary-button" @tap="goLogin">登录</button>
      <button class="secondary-button" @tap="goRegister">注册账号</button>
    </view>

    <view v-else>
      <view v-if="loading" class="profile-status">正在加载个人资料...</view>
      <view v-else class="profile-card">
        <view class="field">
          <text class="field-label">账号</text>
          <text class="field-static">{{ form.username }}</text>
        </view>
        <view class="field">
          <text class="field-label">昵称</text>
          <input class="field-input" :value="form.nickname" @input="form.nickname = $event.detail.value" />
        </view>
        <view class="field">
          <text class="field-label">邮箱</text>
          <input class="field-input" :value="form.email" placeholder="可选" @input="form.email = $event.detail.value" />
        </view>

        <text v-if="message" class="message" :class="{ error: messageType === 'error' }">{{ message }}</text>
        <button class="primary-button" :disabled="saving" @tap="save">{{ saving ? '保存中...' : '保存资料' }}</button>
      </view>

      <view class="quick-list">
        <button class="quick-row" @tap="openSubPage('/pages/profile/meal-plans')">
          <text class="quick-title">我的配菜方案</text>
          <text class="quick-meta">查看已保存方案</text>
        </button>
        <button class="quick-row" @tap="openSubPage('/pages/profile/comments')">
          <text class="quick-title">我的评论</text>
          <text class="quick-meta">查看审核状态</text>
        </button>
        <button class="quick-row" @tap="openSubPage('/pages/profile/reports')">
          <text class="quick-title">我的举报</text>
          <text class="quick-meta">跟进处理结果</text>
        </button>
      </view>

      <button class="logout-button" @tap="logout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMe, logout as clearSession, updateMe } from '../../services/auth-api'
import { getAccessToken, getCurrentUser } from '../../services/auth-storage'

const form = reactive({ username: '', nickname: '', email: '' })
const loading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')
const loggedIn = ref(Boolean(getAccessToken()))
const displayName = computed(() => form.nickname || form.username || '我的')
const initial = computed(() => (loggedIn.value ? displayName.value : '我').slice(0, 1))

function showError(cause, fallback) {
  const data = cause?.response
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object') {
    const value = Object.values(data)[0]
    if (Array.isArray(value)) return value[0]
    if (typeof value === 'string') return value
  }
  return fallback
}

async function load() {
  loggedIn.value = Boolean(getAccessToken())
  message.value = ''
  if (!loggedIn.value) {
    Object.assign(form, { username: '', nickname: '', email: '' })
    return
  }
  const cached = getCurrentUser()
  if (cached) Object.assign(form, cached)
  loading.value = true
  try {
    const user = await getMe()
    Object.assign(form, user)
  } catch (cause) {
    messageType.value = 'error'
    message.value = showError(cause, '个人资料加载失败。')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  message.value = ''
  try {
    const user = await updateMe({ nickname: form.nickname, email: form.email })
    Object.assign(form, user)
    messageType.value = 'success'
    message.value = '资料已保存。'
  } catch (cause) {
    messageType.value = 'error'
    message.value = showError(cause, '保存失败，请稍后重试。')
  } finally {
    saving.value = false
  }
}

function goLogin() {
  uni.navigateTo({ url: '/pages/auth/login?next=%2Fpages%2Fprofile%2Findex' })
}

function goRegister() {
  uni.navigateTo({ url: '/pages/auth/register?next=%2Fpages%2Fprofile%2Findex' })
}

function openSubPage(url) {
  uni.navigateTo({ url })
}

function logout() {
  clearSession()
  loggedIn.value = false
  Object.assign(form, { username: '', nickname: '', email: '' })
  uni.showToast({ title: '已退出登录', icon: 'success' })
}

onShow(load)
</script>

<style scoped>
.profile-page { min-height: 100vh; padding: 28rpx 28rpx calc(120rpx + env(safe-area-inset-bottom)); background: #f7f4ee; }
.profile-hero { display: flex; align-items: center; gap: 22rpx; padding: 28rpx 0 34rpx; }
.avatar { display: flex; align-items: center; justify-content: center; width: 104rpx; height: 104rpx; border-radius: 50%; background: #254f47; color: #fff; font-size: 42rpx; font-weight: 900; }
.profile-copy { flex: 1; min-width: 0; }
.profile-title { display: block; color: #25221d; font-size: 42rpx; font-weight: 900; }
.profile-subtitle { display: block; margin-top: 10rpx; color: #766e63; font-size: 25rpx; line-height: 1.4; }
.guest-panel, .profile-card, .quick-list { padding: 28rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.guest-panel { display: flex; flex-direction: column; gap: 18rpx; }
.profile-status { padding: 50rpx 0; color: #766e63; text-align: center; font-size: 26rpx; }
.field { margin-top: 24rpx; }
.field:first-child { margin-top: 0; }
.field-label { display: block; margin-bottom: 10rpx; color: #4d473f; font-size: 25rpx; font-weight: 700; }
.field-static { display: block; min-height: 58rpx; color: #25221d; font-size: 28rpx; line-height: 58rpx; }
.field-input { width: 100%; height: 82rpx; padding: 0 22rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; color: #25221d; font-size: 28rpx; }
.message { display: block; margin-top: 18rpx; color: #4a7652; font-size: 24rpx; }
.message.error { color: #b6492b; }
.primary-button, .secondary-button { height: 82rpx; border-radius: 8rpx; font-size: 28rpx; font-weight: 800; }
.primary-button { margin-top: 28rpx; background: #254f47; color: #fff; }
.guest-panel .primary-button { margin-top: 0; }
.primary-button[disabled] { opacity: .55; }
.secondary-button { border: 2rpx solid #d9cbb8; color: #254f47; }
.quick-list { margin-top: 22rpx; padding: 0; overflow: hidden; }
.quick-row { display: flex; align-items: center; justify-content: space-between; gap: 18rpx; width: 100%; min-height: 96rpx; padding: 0 26rpx; border-bottom: 2rpx solid #efe5d6; text-align: left; }
.quick-row:last-child { border-bottom: 0; }
.quick-title { color: #25221d; font-size: 28rpx; font-weight: 800; }
.quick-meta { color: #8a7e6d; font-size: 23rpx; }
.logout-button { height: 78rpx; margin-top: 24rpx; color: #b6492b; font-size: 26rpx; font-weight: 700; }
</style>
