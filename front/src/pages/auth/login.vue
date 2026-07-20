<template>
  <view class="auth-page">
    <view class="auth-topbar">
      <button class="back-button" @tap="goBack">返回</button>
      <text class="auth-brand">家常主厨</text>
    </view>
    <view class="auth-card">
      <text class="auth-title">登录</text>
      <text class="auth-subtitle">登录后同步你的个人信息</text>

      <view class="field">
        <text class="field-label">账号</text>
        <input class="field-input" :value="form.username" placeholder="请输入账号" @input="form.username = $event.detail.value" />
      </view>
      <view class="field">
        <text class="field-label">密码</text>
        <input class="field-input" password :value="form.password" placeholder="请输入密码" @input="form.password = $event.detail.value" @confirm="submit" />
      </view>

      <text v-if="error" class="error-message">{{ error }}</text>
      <button class="primary-button" :disabled="loading" @tap="submit">{{ loading ? '登录中...' : '登录' }}</button>
      <button class="link-button" @tap="goRegister">还没有账号？注册</button>
    </view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app'
import { reactive, ref } from 'vue'
import { login } from '../../services/auth-api'
import { openAfterAuth } from '../../services/navigation'

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const nextUrl = ref('/pages/index/index')

function messageFromError(cause) {
  const data = cause?.response
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object') {
    const value = Object.values(data)[0]
    if (Array.isArray(value)) return value[0]
    if (typeof value === 'string') return value
  }
  return '登录失败，请检查账号和密码。'
}

async function submit() {
  if (!form.username || !form.password) {
    error.value = '请输入账号和密码。'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await login(form.username.trim(), form.password)
    openAfterAuth(nextUrl.value)
  } catch (cause) {
    error.value = messageFromError(cause)
  } finally {
    loading.value = false
  }
}

function goBack() {
  uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) })
}

function goRegister() {
  uni.navigateTo({ url: `/pages/auth/register?next=${encodeURIComponent(nextUrl.value)}` })
}

onLoad((options) => {
  if (!options.next) return
  let value = options.next
  try {
    value = decodeURIComponent(value)
  } catch {
    return
  }
  if (value.startsWith('/pages/')) nextUrl.value = value
})
</script>

<style scoped>
.auth-page { min-height: 100vh; padding: 28rpx; background: #f7f4ee; }
.auth-topbar { display: flex; align-items: center; min-height: 72rpx; }
.back-button { width: 96rpx; color: #254f47; font-size: 26rpx; text-align: left; }
.auth-brand { color: #254f47; font-size: 28rpx; font-weight: 800; }
.auth-card { margin-top: 110rpx; padding: 34rpx 28rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffaf2; }
.auth-title { display: block; color: #25221d; font-size: 48rpx; font-weight: 900; }
.auth-subtitle { display: block; margin-top: 12rpx; color: #766e63; font-size: 25rpx; }
.field { margin-top: 28rpx; }
.field-label { display: block; margin-bottom: 10rpx; color: #4d473f; font-size: 25rpx; font-weight: 700; }
.field-input { width: 100%; height: 82rpx; padding: 0 22rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; color: #25221d; font-size: 28rpx; }
.error-message { display: block; margin-top: 18rpx; color: #b6492b; font-size: 24rpx; line-height: 1.45; }
.primary-button { height: 82rpx; margin-top: 30rpx; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 28rpx; font-weight: 800; }
.primary-button[disabled] { opacity: .55; }
.link-button { margin-top: 24rpx; color: #9b4a32; font-size: 25rpx; }
</style>
