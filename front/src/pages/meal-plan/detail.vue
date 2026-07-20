<template>
  <view class="detail-page" v-if="plan">
    <view class="header">
      <text class="title">{{ plan.title }}</text>
      <text class="summary">{{ plan.summary }}</text>
      <view class="metrics">
        <view class="metric">
          <text class="metric-value">{{ plan.servings }}</text>
          <text class="metric-label">人份</text>
        </view>
        <view class="metric">
          <text class="metric-value">{{ plan.items.length }}</text>
          <text class="metric-label">道菜</text>
        </view>
        <view class="metric">
          <text class="metric-value">{{ plan.totalMinutes }}</text>
          <text class="metric-label">分钟</text>
        </view>
      </view>
      <button class="save-button" :disabled="saving" @tap="save">{{ plan.isSaved ? '已保存' : saving ? '保存中...' : '保存方案' }}</button>
      <text v-if="notice" class="notice">{{ notice }}</text>
    </view>

    <view class="section">
      <text class="section-title">菜品</text>
      <view class="dish-list">
        <view v-for="item in plan.items" :key="item.id" class="dish-card">
          <image class="dish-image" :src="item.coverUrl || '/static/images/tomato-egg.png'" mode="aspectFill" />
          <view class="dish-body">
            <view class="dish-topline">
              <text class="dish-name">{{ item.name }}</text>
              <text class="dish-time">{{ item.cookingMinutes || '-' }} 分钟</text>
            </view>
            <text class="dish-reason">{{ item.reason }}</text>
            <view class="dish-actions">
              <button class="small-button" @tap="openRecipe(item.recipeId)">教程</button>
              <button class="small-button ghost" :disabled="replacingId === item.id" @tap="replaceItem(item.id)">
                {{ replacingId === item.id ? '替换中' : '换一道' }}
              </button>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">材料清单</text>
      <view v-if="shoppingList.length === 0" class="empty">暂无材料清单</view>
      <view v-else class="shopping-list">
        <view v-for="group in shoppingList" :key="group.name" class="shopping-row">
          <text class="shopping-name">{{ group.name }}</text>
          <text class="shopping-items">{{ group.items.join('、') }}</text>
        </view>
      </view>
    </view>
  </view>
  <view v-else class="missing">
    <text class="missing-title">{{ loading ? '正在加载方案...' : '没有找到方案' }}</text>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getAccessToken } from '../../services/auth-storage'
import { getMealPlan, replaceMealPlanItem, saveMealPlan } from '../../services/meal-plan-api'

const plan = ref(null)
const loading = ref(false)
const saving = ref(false)
const replacingId = ref('')
const notice = ref('')
const shoppingList = computed(() => plan.value?.shoppingList || [])

async function load(id) {
  loading.value = true
  try {
    plan.value = await getMealPlan(id)
    uni.setNavigationBarTitle({ title: plan.value.title || '配菜方案' })
  } catch {
    notice.value = '方案加载失败。'
  } finally {
    loading.value = false
  }
}

function openRecipe(recipeId) {
  uni.navigateTo({ url: `/pages/recipe/detail?id=${recipeId}` })
}

function requireLogin() {
  if (getAccessToken()) return true
  uni.showModal({
    title: '需要登录',
    content: '登录后可以保存配菜方案。',
    confirmText: '去登录',
    success(result) {
      if (!result.confirm) return
      const next = encodeURIComponent(`/pages/meal-plan/detail?id=${plan.value.id}`)
      uni.navigateTo({ url: `/pages/auth/login?next=${next}` })
    }
  })
  return false
}

async function save() {
  if (plan.value.isSaved) return
  if (!requireLogin()) return
  saving.value = true
  notice.value = ''
  try {
    plan.value = await saveMealPlan(plan.value.id)
    notice.value = '方案已保存到我的。'
  } catch {
    notice.value = '保存失败，请稍后重试。'
  } finally {
    saving.value = false
  }
}

async function replaceItem(itemId) {
  replacingId.value = itemId
  notice.value = ''
  try {
    plan.value = await replaceMealPlanItem(plan.value.id, itemId)
  } catch {
    notice.value = '替换失败，请稍后重试。'
  } finally {
    replacingId.value = ''
  }
}

onLoad((options) => {
  if (options.id) load(options.id)
})
</script>

<style scoped>
.detail-page { min-height: 100vh; padding: 28rpx 28rpx 70rpx; background: #fffaf2; }
.header { padding: 10rpx 0 22rpx; }
.title { display: block; color: #25221d; font-size: 46rpx; font-weight: 900; line-height: 1.18; }
.summary { display: block; margin-top: 16rpx; color: #625a4f; font-size: 27rpx; line-height: 1.55; }
.metrics { display: flex; gap: 14rpx; margin-top: 24rpx; }
.metric { flex: 1; padding: 18rpx 10rpx; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #f7f0e4; text-align: center; }
.metric-value { display: block; color: #c55335; font-size: 31rpx; font-weight: 900; }
.metric-label { display: block; margin-top: 6rpx; color: #776d5f; font-size: 22rpx; }
.save-button { height: 82rpx; margin-top: 24rpx; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 28rpx; font-weight: 900; }
.save-button[disabled] { opacity: .6; }
.notice { display: block; margin-top: 14rpx; color: #8b6a49; font-size: 24rpx; }
.section { margin-top: 30rpx; }
.section-title { display: block; margin-bottom: 18rpx; color: #25221d; font-size: 32rpx; font-weight: 900; }
.dish-list { display: flex; flex-direction: column; gap: 18rpx; }
.dish-card { display: flex; overflow: hidden; border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffdf8; }
.dish-image { flex: 0 0 188rpx; width: 188rpx; height: 188rpx; background: #eee4d5; }
.dish-body { flex: 1; min-width: 0; padding: 20rpx; }
.dish-topline { display: flex; align-items: center; justify-content: space-between; gap: 14rpx; }
.dish-name { min-width: 0; color: #25221d; font-size: 29rpx; font-weight: 900; }
.dish-time { flex: 0 0 auto; color: #c55335; font-size: 22rpx; font-weight: 800; }
.dish-reason { display: block; margin-top: 10rpx; color: #6b6255; font-size: 23rpx; line-height: 1.4; }
.dish-actions { display: flex; gap: 14rpx; margin-top: 14rpx; }
.small-button { min-width: 104rpx; height: 54rpx; padding: 0 18rpx; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 23rpx; font-weight: 800; }
.small-button.ghost { border: 2rpx solid #d9cbb8; background: transparent; color: #254f47; }
.shopping-list { border: 2rpx solid #eadfcd; border-radius: 8rpx; background: #fffdf8; overflow: hidden; }
.shopping-row { padding: 20rpx 24rpx; border-bottom: 2rpx solid #efe5d6; }
.shopping-row:last-child { border-bottom: 0; }
.shopping-name { display: block; color: #25221d; font-size: 26rpx; font-weight: 900; }
.shopping-items { display: block; margin-top: 8rpx; color: #6b6255; font-size: 24rpx; line-height: 1.45; }
.empty, .missing { padding: 70rpx 20rpx; color: #766e63; text-align: center; font-size: 26rpx; }
.missing { min-height: 100vh; background: #f7f4ee; }
.missing-title { color: #25221d; font-size: 32rpx; font-weight: 900; }
</style>
