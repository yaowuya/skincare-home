<template>
  <div class="product-detail" v-if="product">
    <div class="detail-layout">
      <div class="detail-image">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
        <div v-else class="no-image">暂无图片</div>
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
defineProps({
  product: { type: Object, default: null },
})
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
