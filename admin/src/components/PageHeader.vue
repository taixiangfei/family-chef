<template>
  <div class="page-head">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
    </div>
    <div class="page-actions"><slot /></div>
  </div>
</template>

<script setup>
defineProps({ title: String, description: String })
</script>
