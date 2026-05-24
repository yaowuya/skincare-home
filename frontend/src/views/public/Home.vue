<template>
  <div class="home-page">
    <section class="hero">
      <h1 class="hero-title">新品速递</h1>
      <p class="hero-subtitle">发现最新护肤产品，探索美妆趋势</p>
    </section>

    <div class="content-area">
      <el-card shadow="never" class="filter-card">
        <FilterChips :groups="filterGroups" @change="onFilterChange" />
      </el-card>

      <div v-loading="loading" class="masonry-grid">
        <ProductCard
          v-for="product in products"
          :key="product.id"
          :product="product"
          @click="openDetail"
        />
      </div>

      <el-empty v-if="!loading && products.length === 0" description="暂无产品" />

      <div class="load-more" v-if="hasMore">
        <el-button @click="loadMore" :loading="loading">加载更多</el-button>
      </div>
    </div>

    <el-dialog v-model="showDetail" width="720px" :title="currentProduct?.name || ''" destroy-on-close>
      <ProductDetail v-if="currentProduct" :product="currentProduct" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productsApi } from '../../api/products'
import { useTagsStore } from '../../store/tags'
import FilterChips from '../../components/FilterChips.vue'
import ProductCard from '../../components/ProductCard.vue'
import ProductDetail from './ProductDetail.vue'

const tagsStore = useTagsStore()
const products = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showDetail = ref(false)
const currentProduct = ref(null)
const filters = ref({})

const hasMore = computed(() => products.value.length < total.value)

const filterGroups = computed(() => [
  { key: 'form_type_id', label: '剂型', items: tagsStore.formTags },
  { key: 'effect_type_id', label: '功效', items: tagsStore.effectTags },
  { key: 'function_type_id', label: '功能', items: tagsStore.functionTags },
])

async function fetchProducts(reset = false) {
  if (reset) {
    page.value = 1
    products.value = []
  }
  loading.value = true
  try {
    const res = await productsApi.list({ page: page.value, per_page: 20, ...filters.value })
    if (reset) {
      products.value = res.data.items
    } else {
      products.value.push(...res.data.items)
    }
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function onFilterChange(newFilters) {
  filters.value = newFilters
  fetchProducts(true)
}

function loadMore() {
  page.value++
  fetchProducts()
}

function openDetail(product) {
  currentProduct.value = product
  showDetail.value = true
}

onMounted(() => {
  tagsStore.fetchTags()
  fetchProducts()
})
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 64px 20px 48px;
  background: linear-gradient(135deg, #f5f3ff 0%, #ffffff 50%, #fff1f2 100%);
}
.hero-title {
  margin: 0 0 8px;
  font-size: 36px;
  font-weight: 700;
  color: #1a56a8;
}
.hero-subtitle {
  margin: 0;
  font-size: 16px;
  color: #909399;
}
.content-area {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px 40px;
}
.filter-card {
  margin-bottom: 24px;
}
.masonry-grid {
  column-count: 3;
  column-gap: 16px;
}
@media (max-width: 900px) {
  .masonry-grid { column-count: 2; }
}
@media (max-width: 600px) {
  .masonry-grid { column-count: 1; }
}
.load-more {
  text-align: center;
  margin-top: 24px;
}
</style>
