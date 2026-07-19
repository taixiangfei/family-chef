<template>
  <view class="profile-page">
    <view class="profile-head">
      <button class="back-button" @tap="goBack">返回</button>
      <text class="profile-title">我的</text>
    </view>

    <view v-if="loading" class="profile-status">正在加载个人资料...</view>
    <view v-else class="profile-card">
      <view class="avatar">{{ (form.nickname || form.username || '我').slice(0, 1) }}</view>
      <text class="account-name">{{ form.username }}</text>

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
      <button class="logout-button" @tap="logout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { reactive, ref } from 'vue'
import { getMe, logout as clearSession, updateMe } from '../../services/auth-api'
import { getAccessToken } from '../../services/auth-storage'

const form = reactive({ username: '', nickname: '', email: '' })
const loading = ref(true)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

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
  if (!getAccessToken()) {
    uni.redirectTo({ url: '/pages/auth/login' })
    return
  }
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

function logout() {
  clearSession()
  uni.reLaunch({ url: '/pages/index/index' })
}

function goBack() {
  uni.navigateBack({ fail: () => uni.reLaunch({ url: '/pages/index/index' }) })
}

onShow(load)
</script>

<style scoped>
.profile-page { min-height: 100vh; padding: 28rpx; background: #f7f4ee; }
.profile-head { display: flex; align-items: center; min-height: 72rpx; }
.back-button { width: 96rpx; color: #254f47; font-size: 26rpx; text-align: left; }
.profile-title { color: #254f47; font-size: 30rpx; font-weight: 800; }
.profile-status { padding: 70rpx 0; color: #766e63; text-align: center; font-size: 26rpx; }
.profile-card { margin-top: 70rpx; padding: 34rpx 28rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.avatar { display: flex; align-items: center; justify-content: center; width: 96rpx; height: 96rpx; margin: -82rpx auto 18rpx; border-radius: 50%; background: #254f47; color: #fff; font-size: 40rpx; font-weight: 900; }
.account-name { display: block; color: #25221d; font-size: 32rpx; font-weight: 800; text-align: center; }
.field { margin-top: 28rpx; }
.field-label { display: block; margin-bottom: 10rpx; color: #4d473f; font-size: 25rpx; font-weight: 700; }
.field-input { width: 100%; height: 82rpx; padding: 0 22rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; color: #25221d; font-size: 28rpx; }
.message { display: block; margin-top: 18rpx; color: #4a7652; font-size: 24rpx; }
.message.error { color: #b6492b; }
.primary-button { height: 82rpx; margin-top: 30rpx; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 28rpx; font-weight: 800; }
.primary-button[disabled] { opacity: .55; }
.logout-button { margin-top: 24rpx; color: #b6492b; font-size: 25rpx; }
</style>
