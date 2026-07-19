<template>
  <view class="page" v-if="recipe">
    <view class="cover-wrap">
      <image class="cover" :src="recipe.image" mode="aspectFill" />
    </view>

    <view class="header">
      <text class="title">{{ recipe.title }}</text>
      <text class="summary">{{ recipe.summary }}</text>
      <text v-if="loading" class="data-status">正在加载后台最新版本...</text>
      <text v-else-if="notice" class="data-status">{{ notice }}</text>
      <view class="metrics">
        <view class="metric">
          <text class="metric-value">{{ recipe.time }}</text>
          <text class="metric-label">分钟</text>
        </view>
        <view class="metric">
          <text class="metric-value">{{ recipe.difficulty }}</text>
          <text class="metric-label">难度</text>
        </view>
        <view class="metric">
          <text class="metric-value">{{ recipe.servings }}</text>
          <text class="metric-label">人份</text>
        </view>
      </view>
      <view class="tags">
        <text v-for="tag in recipe.tags" :key="tag" class="tag">{{ tag }}</text>
        <text class="tag">{{ recipe.method }}</text>
      </view>
    </view>

    <view v-if="recipe.dishId" class="reaction-panel">
      <view class="reaction-actions">
        <button class="reaction-button" :class="{ active: dishReaction === 1 }" @tap="reactToDish(1)">赞 {{ recipe.likeCount || 0 }}</button>
        <button class="reaction-button" :class="{ active: dishReaction === -1 }" @tap="reactToDish(-1)">踩 {{ recipe.dislikeCount || 0 }}</button>
      </view>
      <button class="report-button" @tap="report('dish', recipe.dishId)">举报内容</button>
    </view>

    <view class="panel">
      <text class="panel-title">材料</text>
      <view class="ingredient-list">
        <view v-for="item in recipe.ingredients" :key="item" class="ingredient-item">
          <text class="dot"></text>
          <text class="ingredient-text">{{ item }}</text>
        </view>
      </view>
    </view>

    <view class="panel">
      <text class="panel-title">步骤</text>
      <view class="step-list">
        <view v-for="(step, index) in recipe.steps" :key="step" class="step-item">
          <text class="step-index">{{ index + 1 }}</text>
          <text class="step-text">{{ step }}</text>
        </view>
      </view>
    </view>

    <view class="panel accent">
      <text class="panel-title">火候与经验</text>
      <text v-for="tip in recipe.tips" :key="tip" class="tip-text">{{ tip }}</text>
    </view>

    <view class="source">
      <text class="source-title">参考</text>
      <text class="source-text">本教程基于 {{ recipe.source }} 的菜谱组织方式改写，并为移动端边做边看场景重新拆分。</text>
    </view>

    <view v-if="recipe.dishId" class="comments-panel">
      <view class="comments-head">
        <text class="panel-title">评论</text>
        <text class="comments-count">{{ commentsTotal }} 条</text>
      </view>
      <textarea class="comment-input" :value="commentContent" maxlength="2000" placeholder="说说这道菜做得怎么样" @input="commentContent = $event.detail.value" />
      <button class="comment-submit" :disabled="submitting" @tap="submitComment">{{ submitting ? '提交中...' : '发表评论' }}</button>
      <text v-if="interactionNotice" class="interaction-notice">{{ interactionNotice }}</text>

      <view v-if="commentsLoading" class="comments-empty">正在加载评论...</view>
      <view v-else-if="comments.length === 0" class="comments-empty">还没有公开评论</view>
      <view v-else class="comment-list">
        <view v-for="comment in comments" :key="comment.id" class="comment-item">
          <view class="comment-meta">
            <text class="comment-user">{{ comment.user_display_name || comment.username }}</text>
            <text class="comment-time">{{ formatDate(comment.created_at) }}</text>
          </view>
          <text class="comment-content">{{ comment.content }}</text>
          <view class="comment-actions">
            <button class="comment-action" :class="{ active: comment.my_reaction === 1 }" @tap="reactToComment(comment, 1)">赞 {{ comment.like_count }}</button>
            <button class="comment-action" :class="{ active: comment.my_reaction === -1 }" @tap="reactToComment(comment, -1)">踩 {{ comment.dislike_count }}</button>
            <button class="comment-action report" @tap="report('comment', comment.id)">举报</button>
          </view>
        </view>
      </view>
    </view>
  </view>

  <view class="missing" v-else>
    <text class="missing-title">没有找到这道菜</text>
    <button class="back-button" @tap="goBack">返回首页</button>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getRecipeById } from '../../utils/cookbook'
import { getRecipe } from '../../services/recipe-api'
import { mapRecipeDetail } from '../../services/recipe-adapter'
import { getAccessToken } from '../../services/auth-storage'
import {
  createComment,
  createReport,
  getComments,
  getDishReaction,
  setCommentReaction,
  setDishReaction
} from '../../services/interaction-api'

const recipe = ref(null)
const loading = ref(false)
const notice = ref('')
const comments = ref([])
const commentsTotal = ref(0)
const commentsLoading = ref(false)
const commentContent = ref('')
const submitting = ref(false)
const dishReaction = ref(0)
const interactionNotice = ref('')

function goBack() {
  uni.navigateBack({
    fail() {
      uni.reLaunch({
        url: '/pages/index/index'
      })
    }
  })
}

function requireLogin() {
  if (getAccessToken()) return true
  uni.showModal({
    title: '需要登录',
    content: '登录后可以发表评论、赞踩和举报。',
    confirmText: '去登录',
    success(result) {
      if (!result.confirm) return
      const next = encodeURIComponent(`/pages/recipe/detail?id=${recipe.value.id}`)
      uni.navigateTo({ url: `/pages/auth/login?next=${next}` })
    }
  })
  return false
}

async function loadInteractions() {
  if (!recipe.value?.dishId) return
  commentsLoading.value = true
  try {
    const data = await getComments(recipe.value.dishId)
    comments.value = data.results || data
    commentsTotal.value = data.count ?? comments.value.length
  } catch {
    interactionNotice.value = '评论暂时加载失败。'
  } finally {
    commentsLoading.value = false
  }

  if (getAccessToken()) {
    try {
      const reaction = await getDishReaction(recipe.value.dishId)
      dishReaction.value = reaction.value || 0
      recipe.value.likeCount = reaction.likeCount
      recipe.value.dislikeCount = reaction.dislikeCount
    } catch {
      // Dish content remains usable if reaction state cannot be loaded.
    }
  }
}

async function reactToDish(value) {
  if (!requireLogin()) return
  const nextValue = dishReaction.value === value ? 0 : value
  try {
    const result = await setDishReaction(recipe.value.dishId, nextValue)
    dishReaction.value = result.value
    recipe.value.likeCount = result.likeCount
    recipe.value.dislikeCount = result.dislikeCount
  } catch {
    uni.showToast({ title: '操作失败，请稍后重试', icon: 'none' })
  }
}

async function reactToComment(comment, value) {
  if (!requireLogin()) return
  const nextValue = comment.my_reaction === value ? 0 : value
  try {
    const updated = await setCommentReaction(comment.id, nextValue)
    Object.assign(comment, updated)
  } catch {
    uni.showToast({ title: '操作失败，请稍后重试', icon: 'none' })
  }
}

async function submitComment() {
  if (!requireLogin()) return
  const content = commentContent.value.trim()
  if (!content) {
    interactionNotice.value = '请先输入评论内容。'
    return
  }
  submitting.value = true
  interactionNotice.value = ''
  try {
    await createComment(recipe.value.dishId, content)
    commentContent.value = ''
    interactionNotice.value = '评论已提交，审核通过后会公开展示。'
  } catch {
    interactionNotice.value = '评论提交失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}

function report(targetType, targetId) {
  if (!requireLogin()) return
  const reasons = ['内容错误', '不适内容', '广告或垃圾信息', '其他问题']
  uni.showActionSheet({
    itemList: reasons,
    success: async ({ tapIndex }) => {
      try {
        await createReport(targetType, targetId, reasons[tapIndex])
        uni.showToast({ title: '举报已提交', icon: 'success' })
      } catch {
        uni.showToast({ title: '举报失败，请稍后重试', icon: 'none' })
      }
    }
  })
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN') : ''
}

onLoad(async (options) => {
  recipe.value = getRecipeById(options.id)
  if (recipe.value) {
    uni.setNavigationBarTitle({
      title: recipe.value.title
    })
  }

  loading.value = true
  try {
    const article = await getRecipe(options.id)
    recipe.value = mapRecipeDetail(article)
    uni.setNavigationBarTitle({
      title: recipe.value.title
    })
    loadInteractions()
  } catch {
    if (recipe.value) {
      notice.value = '后台暂时不可用，当前使用本地教程。'
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding-bottom: 56rpx;
  background: #fffaf2;
}

.cover-wrap {
  padding: 24rpx 28rpx 0;
}

.cover {
  width: 100%;
  height: 360rpx;
  border-radius: 8rpx;
  background: #eee1cf;
}

.header {
  padding: 30rpx 28rpx 18rpx;
}

.reaction-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
  margin: 8rpx 28rpx 0;
  padding: 20rpx 0;
  border-top: 2rpx solid #eadfcd;
  border-bottom: 2rpx solid #eadfcd;
}

.reaction-actions { display: flex; gap: 12rpx; }
.reaction-button { min-width: 112rpx; height: 58rpx; padding: 0 16rpx; border: 2rpx solid #d9cbb8; border-radius: 8rpx; color: #5d5142; font-size: 23rpx; }
.reaction-button.active { border-color: #c55335; background: #c55335; color: #fff; }
.report-button { color: #8b7d6a; font-size: 23rpx; }

.title {
  display: block;
  color: #25221d;
  font-size: 46rpx;
  font-weight: 900;
  line-height: 1.18;
}

.summary {
  display: block;
  margin-top: 18rpx;
  color: #625a4f;
  font-size: 28rpx;
  line-height: 1.55;
}

.data-status {
  display: block;
  margin-top: 12rpx;
  color: #8b7d6a;
  font-size: 23rpx;
  line-height: 1.4;
}

.metrics {
  display: flex;
  gap: 14rpx;
  margin-top: 26rpx;
}

.metric {
  flex: 1;
  min-width: 0;
  padding: 18rpx 10rpx;
  border: 2rpx solid #eadfcd;
  border-radius: 8rpx;
  background: #f7f0e4;
  text-align: center;
}

.metric-value {
  display: block;
  color: #c55335;
  font-size: 30rpx;
  font-weight: 900;
}

.metric-label {
  display: block;
  margin-top: 6rpx;
  color: #776d5f;
  font-size: 22rpx;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 20rpx;
}

.tag {
  padding: 8rpx 14rpx;
  border-radius: 6rpx;
  background: #e8f0dc;
  color: #405835;
  font-size: 23rpx;
}

.panel {
  margin: 22rpx 28rpx 0;
  padding: 28rpx;
  border: 2rpx solid #eadfcd;
  border-radius: 8rpx;
  background: #fffdf8;
}

.panel.accent {
  border-color: #e7c7b9;
  background: #fff4ec;
}

.panel-title {
  display: block;
  margin-bottom: 18rpx;
  color: #25221d;
  font-size: 32rpx;
  font-weight: 900;
}

.ingredient-item {
  display: flex;
  align-items: flex-start;
  gap: 14rpx;
  margin-top: 14rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  margin-top: 13rpx;
  border-radius: 50%;
  background: #c55335;
}

.ingredient-text {
  flex: 1;
  color: #4e473e;
  font-size: 28rpx;
  line-height: 1.45;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.step-item {
  display: flex;
  gap: 18rpx;
}

.step-index {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 52rpx;
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: #254f47;
  color: #fff;
  font-size: 25rpx;
  font-weight: 900;
}

.step-text {
  flex: 1;
  color: #403a33;
  font-size: 29rpx;
  line-height: 1.55;
}

.tip-text {
  display: block;
  margin-top: 14rpx;
  color: #5d4437;
  font-size: 27rpx;
  line-height: 1.5;
}

.source {
  margin: 28rpx;
  padding: 24rpx 0 0;
  border-top: 2rpx solid #eadfcd;
}

.source-title,
.source-text {
  display: block;
}

.comments-panel { margin: 34rpx 28rpx 0; padding-top: 26rpx; border-top: 2rpx solid #eadfcd; }
.comments-head { display: flex; align-items: center; justify-content: space-between; }
.comments-head .panel-title { margin-bottom: 0; }
.comments-count { color: #807665; font-size: 23rpx; }
.comment-input { width: 100%; min-height: 150rpx; margin-top: 20rpx; padding: 20rpx; border: 2rpx solid #dfd2bf; border-radius: 8rpx; background: #fffdf8; color: #403a33; font-size: 26rpx; line-height: 1.5; }
.comment-submit { width: 180rpx; height: 64rpx; margin: 16rpx 0 0 auto; border-radius: 8rpx; background: #254f47; color: #fff; font-size: 24rpx; font-weight: 700; }
.comment-submit[disabled] { opacity: .55; }
.interaction-notice { display: block; margin-top: 14rpx; color: #8b6a49; font-size: 23rpx; line-height: 1.4; }
.comments-empty { padding: 42rpx 0; color: #8b8173; font-size: 25rpx; text-align: center; }
.comment-list { margin-top: 28rpx; }
.comment-item { padding: 24rpx 0; border-top: 2rpx solid #eee4d5; }
.comment-meta { display: flex; align-items: center; justify-content: space-between; gap: 18rpx; }
.comment-user { color: #254f47; font-size: 25rpx; font-weight: 800; }
.comment-time { color: #958a7b; font-size: 21rpx; }
.comment-content { display: block; margin-top: 12rpx; color: #403a33; font-size: 27rpx; line-height: 1.55; }
.comment-actions { display: flex; align-items: center; gap: 20rpx; margin-top: 14rpx; }
.comment-action { color: #756a5b; font-size: 22rpx; }
.comment-action.active { color: #c55335; font-weight: 800; }
.comment-action.report { margin-left: auto; color: #958a7b; }

.source-title {
  color: #25221d;
  font-size: 26rpx;
  font-weight: 900;
}

.source-text {
  margin-top: 10rpx;
  color: #766e63;
  font-size: 24rpx;
  line-height: 1.5;
}

.missing {
  min-height: 100vh;
  padding: 80rpx 32rpx;
  background: #f7f4ee;
  text-align: center;
}

.missing-title {
  display: block;
  color: #25221d;
  font-size: 34rpx;
  font-weight: 900;
}

.back-button {
  width: 220rpx;
  height: 80rpx;
  margin: 30rpx auto 0;
  border-radius: 8rpx;
  background: #254f47;
  color: #fff;
  font-size: 28rpx;
}

@media screen and (min-width: 768px) {
  .page {
    max-width: 860px;
    margin: 0 auto;
  }

  .cover {
    height: 420rpx;
  }
}
</style>
