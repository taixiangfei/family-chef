<template>
  <view class="detail-page" v-if="plan">
    <view class="header">
      <text class="eyebrow">今晚菜单</text>
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
      <button class="save-button" :disabled="saving" @tap="save">{{ plan.isSaved ? '已收进菜谱夹' : saving ? '保存中...' : '收进菜谱夹' }}</button>
      <text v-if="notice" class="notice">{{ notice }}</text>
    </view>

    <view class="section">
      <text class="section-title">上桌顺序</text>
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
      <text class="section-title">采买小票</text>
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
.detail-page { min-height: 100vh; padding: 28rpx 28rpx 74rpx; background: linear-gradient(180deg, #fff7ea 0%, #f4ead8 100%); }
.header { padding: 30rpx 28rpx; border: 2rpx solid #d7b485; border-radius: 8rpx; background: #f9e4c2; box-shadow: 0 8rpx 0 #e2c79f; }
.eyebrow { display: block; margin-bottom: 10rpx; color: #a44d32; font-size: 23rpx; font-weight: 900; }
.title { display: block; color: #2b241c; font-size: 46rpx; font-weight: 900; line-height: 1.18; }
.summary { display: block; margin-top: 16rpx; color: #6a4d39; font-size: 27rpx; line-height: 1.55; }
.metrics { display: flex; gap: 14rpx; margin-top: 24rpx; }
.metric { flex: 1; min-width: 0; padding: 18rpx 10rpx; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; text-align: center; }
.metric-value { display: block; color: #c84f31; font-size: 31rpx; font-weight: 900; }
.metric-label { display: block; margin-top: 6rpx; color: #6f4a32; font-size: 22rpx; font-weight: 800; }
.save-button { height: 84rpx; margin-top: 24rpx; border-radius: 8rpx; background: #1f5c4c; color: #fffaf1; font-size: 28rpx; font-weight: 900; }
.save-button[disabled] { opacity: .6; }
.notice { display: block; margin-top: 16rpx; color: #8b6a49; font-size: 24rpx; line-height: 1.45; }
.section { margin-top: 34rpx; }
.section-title { display: block; margin-bottom: 18rpx; color: #2b241c; font-size: 32rpx; font-weight: 900; }
.dish-list { display: flex; flex-direction: column; gap: 20rpx; }
.dish-card { display: flex; overflow: hidden; border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; box-shadow: 0 7rpx 0 #ead4b4; }
.dish-image { flex: 0 0 190rpx; width: 190rpx; height: 196rpx; background: #ead8bd; }
.dish-body { flex: 1; min-width: 0; padding: 20rpx; }
.dish-topline { display: flex; align-items: flex-start; justify-content: space-between; gap: 14rpx; }
.dish-name { min-width: 0; color: #2b241c; font-size: 29rpx; font-weight: 900; line-height: 1.28; }
.dish-time { flex: 0 0 auto; max-width: 106rpx; color: #c84f31; font-size: 22rpx; font-weight: 900; text-align: right; }
.dish-reason { display: block; margin-top: 10rpx; color: #6a4d39; font-size: 23rpx; line-height: 1.4; }
.dish-actions { display: flex; gap: 14rpx; margin-top: 14rpx; }
.small-button { min-width: 104rpx; height: 56rpx; padding: 0 18rpx; border-radius: 8rpx; background: #1f5c4c; color: #fffaf1; font-size: 23rpx; font-weight: 900; }
.small-button.ghost { border: 2rpx solid #d8b98f; background: #fff7ea; color: #1f5c4c; }
.shopping-list { border: 2rpx solid #d8b98f; border-radius: 8rpx; background: #fffaf1; overflow: hidden; }
.shopping-row { padding: 20rpx 24rpx; border-bottom: 2rpx dashed #e5cda9; }
.shopping-row:last-child { border-bottom: 0; }
.shopping-name { display: block; color: #2b241c; font-size: 26rpx; font-weight: 900; }
.shopping-items { display: block; margin-top: 8rpx; color: #6a4d39; font-size: 24rpx; line-height: 1.45; }
.empty, .missing { padding: 70rpx 20rpx; color: #7b604f; text-align: center; font-size: 26rpx; }
.missing { min-height: 100vh; background: #f4ead8; }
.missing-title { color: #2b241c; font-size: 32rpx; font-weight: 900; }
</style>
