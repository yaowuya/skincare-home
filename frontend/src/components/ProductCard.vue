<template>
  <div class="product-card" @click="$emit('click', product)">
    <div class="card-image">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
      <div v-else class="placeholder-image" :style="{ background: placeholderGradient }"></div>
    </div>
    <div class="card-body">
      <div class="tag-row">
        <span v-for="t in (product.form_tags || [])" :key="'f'+t.id" class="badge form">{{ t.name }}</span>
        <span v-for="t in (product.effect_tags || [])" :key="'e'+t.id" class="badge effect">{{ t.name }}</span>
      </div>
      <h3 class="card-title">{{ product.name }}</h3>
      <p class="card-desc">{{ product.description }}</p>
      <div class="card-footer">
        <span class="card-date">{{ product.published_at }}</span>
        <span class="card-arrow">&rarr;</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, required: true },
})
defineEmits(['click'])

const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
]
const placeholderGradient = computed(() => {
  const hash = (props.product.name || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  return gradients[hash % gradients.length]
})
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s;
  break-inside: avoid;
  margin-bottom: 16px;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}
.card-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.product-card:hover .card-image img {
  transform: scale(1.05);
}
.placeholder-image {
  width: 100%;
  height: 100%;
}
.card-body {
  padding: 12px 16px 16px;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}
.badge.form {
  background: #ecf5ff;
  color: #1a56a8;
}
.badge.effect {
  background: #f0f9eb;
  color: #67c23a;
}
.card-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-desc {
  margin: 0 0 10px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-date {
  font-size: 12px;
  color: #c0c4cc;
}
.card-arrow {
  font-size: 16px;
  color: #1a56a8;
  transition: transform 0.2s;
}
.product-card:hover .card-arrow {
  transform: translateX(4px);
}
</style>
