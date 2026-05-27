<template>
  <div class="product-portal">
    <header class="top-nav">
      <nav class="nav-shell">
        <span class="nav-spacer"></span>
        <div class="nav-links">
          <button class="nav-link active" type="button">新品速递</button>
          <button class="nav-link" type="button">原料库</button>
          <button class="nav-link" type="button">策划广场</button>
          <button class="nav-link" type="button">配方库</button>
          <button class="nav-link" type="button">医疗器械</button>
        </div>
        <el-dropdown trigger="click" @command="handleUserCommand">
          <button class="avatar-btn" type="button">
            <el-icon><User /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="authStore.isAdmin" command="manage">管理</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>
    </header>

    <main class="content-area">
      <section class="filter-panel">
        <div v-for="group in filterGroups" :key="group.key" class="filter-row">
          <div class="filter-label">
            <span>{{ group.label }}</span>
          </div>
          <div class="chip-list">
            <button
              class="filter-chip"
              :class="{ active: !filters[group.key] }"
              type="button"
              @click="selectFilter(group.key, '')"
            >
              全部
            </button>
            <button
              v-for="item in group.items"
              :key="item.id"
              class="filter-chip"
              :class="{ active: filters[group.key] === item.id }"
              type="button"
              @click="selectFilter(group.key, item.id)"
            >
              {{ item.name }}
            </button>
          </div>
        </div>
        <div class="filter-summary">
          <span>显示 {{ total }} 个符合您标准的商品。</span>
        </div>
      </section>

      <section v-loading="loading" class="product-grid">
        <article
          v-for="(product, index) in products"
          :key="product.id"
          class="product-card"
          @click="openDetail(product)"
        >
          <div v-if="index === 0" class="card-ribbon">新品</div>
          <div v-else-if="index === 2" class="card-ribbon">热点推荐</div>
          <div class="product-image">
            <img v-if="coverOf(product)" :src="coverOf(product)" :alt="product.name" />
            <div v-else class="image-fallback">
              <el-icon :size="34"><Picture /></el-icon>
            </div>
          </div>
          <div class="card-body">
            <div class="tag-row">
              <span v-if="firstTag(product.form_tags)" class="tag primary">{{ firstTag(product.form_tags) }}</span>
              <span v-if="effectText(product)" class="tag">{{ effectText(product) }}</span>
            </div>
            <h2>{{ product.name }}</h2>
            <p>{{ product.description || product.ingredients || '暂无产品说明。' }}</p>
            <div class="card-footer">
              <span>
                <el-icon><Calendar /></el-icon>
                {{ formatDate(product.published_at) }}
              </span>
              <span class="arrow">
                <el-icon><ArrowRight /></el-icon>
              </span>
            </div>
          </div>
        </article>
      </section>

      <el-empty v-if="!loading && products.length === 0" description="暂无产品" />

      <div v-if="hasMore" class="load-more">
        <button type="button" :disabled="loading" @click="loadMore">
          {{ loading ? '加载中...' : '加载更多产品' }}
          <el-icon><ArrowDown /></el-icon>
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, ArrowRight, Calendar, Filter, MagicStick, Picture, User } from '@element-plus/icons-vue'
import { productsApi } from '../../api/products'
import { useTagsStore } from '../../store/tags'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
const tagsStore = useTagsStore()
const authStore = useAuthStore()
const products = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const filters = reactive({
  form_type_id: '',
  effect_type_id: '',
  function_type_id: '',
})

const hasMore = computed(() => products.value.length < total.value)

const filterGroups = computed(() => [
  { key: 'form_type_id', label: '剂型分类', icon: Filter, items: tagsStore.formTags },
  { key: 'effect_type_id', label: '功效分类', icon: MagicStick, items: tagsStore.effectTags },
  { key: 'function_type_id', label: '功能分类', icon: Picture, items: tagsStore.functionTags },
])

async function fetchProducts(reset = false) {
  if (reset) {
    page.value = 1
    products.value = []
  }
  loading.value = true
  try {
    const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value))
    const res = await productsApi.list({ page: page.value, per_page: 20, sort_by: 'created_at', sort_order: 'desc', ...params })
    products.value = reset ? res.data.items : [...products.value, ...res.data.items]
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function selectFilter(key, id) {
  filters[key] = id
  fetchProducts(true)
}

function loadMore() {
  page.value += 1
  fetchProducts()
}

function openDetail(product) {
  router.push(`/products/${product.id}`)
}

function handleUserCommand(command) {
  if (command === 'manage') {
    router.push('/admin/products')
    return
  }
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

function coverOf(product) {
  return product.images?.[0]?.url || product.image_url || product.image || ''
}

function firstTag(tags = []) {
  return tags[0]?.name || ''
}

function effectText(product) {
  return (product.effect_tags || []).slice(0, 2).map((tag) => tag.name).join(' / ')
}

function formatDate(date) {
  return date ? String(date).replaceAll('-', '.') : '未发布'
}

onMounted(() => {
  tagsStore.fetchTags()
  fetchProducts(true)
})
</script>

<style scoped>
.product-portal {
  min-height: 100vh;
  background: #f8f9fa;
  color: #191c1d;
}
.top-nav {
  position: fixed;
  top: 14px;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  justify-content: center;
  padding: 0 16px;
}
.nav-shell {
  width: min(1280px, calc(100% - 32px));
  height: 60px;
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: 10px;
  padding: 5px 10px;
  border: 1px solid rgba(195, 198, 209, 0.42);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 8px 20px rgba(0, 51, 102, 0.05);
  backdrop-filter: blur(12px);
}
.nav-links {
  display: flex;
  justify-content: center;
  gap: 6px;
  overflow-x: auto;
}
.nav-link {
  height: 42px;
  padding: 0 24px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #43474f;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}
.nav-link.active {
  background: #fff;
  color: #001e40;
  box-shadow: 0 6px 14px rgba(0, 51, 102, 0.07);
}
.avatar-btn {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 2px solid #fff;
  border-radius: 999px;
  background: #d5e3ff;
  color: #003366;
  cursor: pointer;
}
.content-area {
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
  padding-top: 98px;
  padding-bottom: 64px;
}
.filter-panel {
  position: relative;
  z-index: 3;
  padding: 28px 32px;
  border: 1px solid rgba(195, 198, 209, 0.5);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 16px 36px rgba(0, 51, 102, 0.08);
  backdrop-filter: blur(16px);
}
.filter-row {
  display: grid;
  grid-template-columns: 128px 1fr;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(195, 198, 209, 0.32);
}
.filter-row:last-of-type {
  border-bottom: 0;
}
.filter-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  color: #4b5563;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0;
}
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.filter-chip {
  min-width: 68px;
  height: 38px;
  padding: 0 18px;
  border: 1px solid rgba(115, 119, 128, 0.34);
  border-radius: 999px;
  background: #fff;
  color: #43474f;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}
.filter-chip:hover {
  border-color: #003366;
  color: #003366;
}
.filter-chip.active {
  border-color: #003366;
  background: #003366;
  color: #fff;
  box-shadow: 0 6px 14px rgba(0, 51, 102, 0.14);
}
.filter-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-top: 14px;
  color: #737780;
  font-size: 12px;
}
.filter-summary button {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 0;
  background: transparent;
  color: #003366;
  font-weight: 700;
  cursor: pointer;
}
.filter-summary button:hover {
  background: rgba(0, 51, 102, 0.08);
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 22px;
  margin-top: 44px;
}
.product-card {
  position: relative;
  display: block;
  width: 100%;
  margin: 0;
  overflow: hidden;
  border: 1px solid rgba(195, 198, 209, 0.5);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 12px 28px rgba(0, 51, 102, 0.06);
  cursor: pointer;
  transition: transform 0.28s ease, box-shadow 0.28s ease;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 51, 102, 0.12);
}
.card-ribbon {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 2;
  padding: 7px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.92);
  color: #003366;
  font-size: 13px;
  font-weight: 700;
}
.product-image {
  position: relative;
  aspect-ratio: 0.95;
  overflow: hidden;
  background: #e7e8e9;
}
.product-image img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  transition: transform 0.7s ease;
}
.product-card:hover .product-image img {
  transform: scale(1.045);
}
.image-fallback {
  height: 100%;
  display: grid;
  place-items: center;
  color: #737780;
}
.card-body {
  padding: 16px 18px 18px;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.tag {
  padding: 4px 9px;
  border-radius: 5px;
  background: rgba(225, 227, 228, 0.55);
  color: #43474f;
  font-size: 12px;
  line-height: 1.3;
}
.tag.primary {
  border: 1px solid rgba(167, 200, 255, 0.8);
  background: rgba(213, 227, 255, 0.55);
  color: #003366;
}
.card-body h2 {
  margin: 0 0 8px;
  color: #191c1d;
  font-size: 20px;
  line-height: 1.25;
}
.card-body p {
  display: -webkit-box;
  min-height: 44px;
  margin: 0;
  overflow: hidden;
  color: #43474f;
  font-size: 14px;
  line-height: 1.6;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(195, 198, 209, 0.35);
}
.card-footer span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #737780;
  font-size: 12px;
}
.arrow {
  width: 30px;
  height: 30px;
  justify-content: center;
  border-radius: 999px;
  background: #f3f4f5;
  transition: all 0.2s ease;
}
.product-card:hover .arrow {
  background: #003366;
  color: #fff;
}
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}
.load-more button {
  height: 52px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0 34px;
  border: 1px solid rgba(115, 119, 128, 0.3);
  border-radius: 999px;
  background: #fff;
  color: #003366;
  font-weight: 800;
  cursor: pointer;
}
@media (max-width: 760px) {
  .nav-shell {
    grid-template-columns: 1fr 38px;
  }
  .nav-spacer {
    display: none;
  }
  .nav-links {
    justify-content: flex-start;
  }
  .nav-link {
    padding: 0 16px;
  }
  .filter-panel {
    padding: 20px;
  }
  .filter-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .filter-summary {
    align-items: flex-start;
    flex-direction: column;
  }
  .product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
}

@media (max-width: 1280px) {
  .product-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1080px) {
  .product-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
