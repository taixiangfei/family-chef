<template>
  <view class="page" v-if="recipe">
    <view class="cover-wrap">
      <image class="cover" :src="recipe.image" mode="aspectFill" />
    </view>

    <view class="header">
      <text class="title">{{ recipe.title }}</text>
      <text class="summary">{{ recipe.summary }}</text>
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

const recipe = ref(null)

function goBack() {
  uni.navigateBack({
    fail() {
      uni.reLaunch({
        url: '/pages/index/index'
      })
    }
  })
}

onLoad((options) => {
  recipe.value = getRecipeById(options.id)
  if (recipe.value) {
    uni.setNavigationBarTitle({
      title: recipe.value.title
    })
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
