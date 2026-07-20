<template>
  <span class="status-tag" :class="`status-${status}`">{{ labels[status] || status || '-' }}</span>
</template>

<script setup>
defineProps({ status: String })
const labels = {
  active: '正常', disabled: '已禁用', locked: '已锁定', pending_delete: '待注销', deleted: '已删除',
  draft: '草稿', pending_review: '待审核', rejected: '已驳回', published: '已发布', unpublished: '已下架', archived: '已归档',
  pending: '待处理', visible: '可见', hidden: '已隐藏', resolved: '已处理', dismissed: '已驳回'
}
</script>
