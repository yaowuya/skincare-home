<template>
  <div class="product-detail" v-if="product">
    <div class="detail-layout">
      <div class="detail-image">
        <img v-if="coverImage" :src="coverImage" :alt="product.name" />
        <div v-else class="no-image">暂无图片</div>
        <div v-if="galleryImages.length > 1" class="image-thumbs">
          <button
            v-for="image in galleryImages"
            :key="image.id || image.url"
            class="thumb-btn"
            :class="{ active: image.url === coverImage }"
            type="button"
            @click="coverImage = image.url"
          >
            <img :src="image.url" :alt="product.name" />
          </button>
        </div>
      </div>
      <div class="detail-info">
        <h2 class="detail-name">{{ product.name }}</h2>
        <div class="detail-date" v-if="product.published_at">{{ product.published_at }}</div>

        <div class="detail-tags" v-if="product.form_tags?.length">
          <span class="tag-label">剂型：</span>
          <el-tag v-for="t in product.form_tags" :key="t.id" size="small" type="primary" style="margin: 2px">{{ t.name }}</el-tag>
        </div>
        <div class="detail-tags" v-if="product.effect_tags?.length">
          <span class="tag-label">功效：</span>
          <el-tag v-for="t in product.effect_tags" :key="t.id" size="small" type="success" style="margin: 2px">{{ t.name }}</el-tag>
        </div>
        <div class="detail-tags" v-if="product.function_tags?.length">
          <span class="tag-label">功能：</span>
          <el-tag v-for="t in product.function_tags" :key="t.id" size="small" type="warning" style="margin: 2px">{{ t.name }}</el-tag>
        </div>

        <div class="detail-section" v-if="product.description">
          <h4>产品描述</h4>
          <p>{{ product.description }}</p>
        </div>
        <div class="detail-section" v-if="product.ingredients">
          <h4>成分</h4>
          <p>{{ product.ingredients }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  product: { type: Object, default: null },
})

const coverImage = ref('')
const galleryImages = computed(() => props.product?.images || [])

watch(
  () => props.product,
  (product) => {
    coverImage.value = product?.images?.[0]?.url || product?.image_url || product?.image || ''
  },
  { immediate: true }
)
</script>

<style scoped>
.detail-layout {
  display: flex;
  gap: 32px;
}
.detail-image {
  flex: 0 0 320px;
}
.detail-image img {
  width: 100%;
  border-radius: 8px;
  object-fit: cover;
}
.image-thumbs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(56px, 1fr));
  gap: 8px;
  margin-top: 10px;
}
.thumb-btn {
  aspect-ratio: 1;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  overflow: hidden;
}
.thumb-btn.active {
  border-color: #1a56a8;
}
.thumb-btn img {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  display: block;
}
.no-image {
  width: 320px;
  height: 240px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}
.detail-info {
  flex: 1;
  min-width: 0;
}
.detail-name {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}
.detail-date {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
}
.detail-tags {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
.tag-label {
  font-size: 13px;
  color: #606266;
  margin-right: 4px;
}
.detail-section {
  margin-top: 20px;
}
.detail-section h4 {
  margin: 0 0 8px;
  font-size: 15px;
  color: #303133;
}
.detail-section p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  white-space: pre-wrap;
}
@media (max-width: 700px) {
  .detail-layout {
    flex-direction: column;
  }
  .detail-image {
    flex: none;
  }
}
</style>
