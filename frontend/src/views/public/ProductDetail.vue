<template>
  <div class="detail-page" v-loading="loading">
    <!-- Header -->
    <header class="detail-header">
      <div class="header-inner">
        <router-link class="brand" to="/">CosmeticLab</router-link>
        <el-dropdown trigger="click" @command="handleUserCommand">
          <button class="avatar-btn" type="button">
            <img
              v-if="authStore.user"
              :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(authStore.user.username)}&background=d5e3ff&color=003366&size=40`"
              alt="User"
            />
            <el-icon v-else><User /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="authStore.isAdmin" command="manage">
                <el-icon><Setting /></el-icon>
                管理
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- Main Content -->
    <main v-if="detailProduct" class="detail-main">
      <!-- Breadcrumbs -->
      <nav class="crumbs">
        <router-link to="/">首页</router-link>
        <el-icon><ArrowRight /></el-icon>
        <router-link to="/">新品速递</router-link>
        <el-icon><ArrowRight /></el-icon>
        <span class="crumbs-current">{{ detailProduct.name }}</span>
      </nav>

      <!-- Split Layout -->
      <div class="split-layout">
        <!-- Left: Gallery (7 cols) -->
        <div class="gallery-col" @mouseenter="isGalleryHovered = true" @mouseleave="isGalleryHovered = false">
          <div class="hero-image">
            <el-image
              v-if="coverImage"
              :src="coverImage"
              :preview-src-list="previewSrcList"
              :initial-index="currentImageIndex"
              fit="cover"
              class="hero-preview-image"
            />
            <div v-else class="no-image">
              <el-icon :size="48"><Picture /></el-icon>
            </div>
          </div>
          <div class="thumb-row">
            <button
              v-for="(image, idx) in galleryImages"
              :key="image.id || image.url"
              class="thumb"
              :class="{ active: idx === currentImageIndex }"
              type="button"
              @click="selectImage(idx)"
            >
              <img :src="image.url" :alt="`${detailProduct.name} ${idx + 1}`" />
            </button>
            <div v-if="galleryImages.length === 0" class="thumb empty-thumb">
              <el-icon><Picture /></el-icon>
            </div>
          </div>
        </div>

        <!-- Right: Info (5 cols) -->
        <div class="info-col">
          <!-- Product Title -->
          <div class="title-section">
            <h1>{{ detailProduct.name }}</h1>
          </div>

          <!-- Info Card -->
          <div class="info-card">
            <!-- Publish Date -->
            <div v-if="detailProduct.published_at" class="date-badge">
              <el-icon><Calendar /></el-icon>
              <span>发布日期: {{ detailProduct.published_at }}</span>
            </div>

            <!-- Tags Grid -->
            <div class="tags-grid">
              <div v-if="detailProduct.form_tags?.length" class="tag-group">
                <span class="tag-label">剂型</span>
                <div class="tag-list">
                  <span v-for="tag in detailProduct.form_tags" :key="tag.id" class="tag-pill form">{{ tag.name }}</span>
                </div>
              </div>
              <div v-if="detailProduct.effect_tags?.length" class="tag-group">
                <span class="tag-label">功效</span>
                <div class="tag-list">
                  <span v-for="tag in detailProduct.effect_tags" :key="tag.id" class="tag-pill effect">{{ tag.name }}</span>
                </div>
              </div>
              <div v-if="detailProduct.function_tags?.length" class="tag-group">
                <span class="tag-label">功能</span>
                <div class="tag-list">
                  <span v-for="tag in detailProduct.function_tags" :key="tag.id" class="tag-pill function">{{ tag.name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div v-if="detailProduct.description" class="section-block">
            <h3 class="section-heading">
              <el-icon><Document /></el-icon>
              产品描述
            </h3>
            <p class="desc-text">{{ detailProduct.description }}</p>
          </div>

          <!-- Ingredients -->
          <div v-if="detailProduct.ingredients" class="section-block">
            <h3 class="section-heading">
              <el-icon><MagicStick /></el-icon>
              核心成分
            </h3>
            <div class="ingredients-grid">
              <div
                v-for="(item, idx) in ingredientItems"
                :key="idx"
                class="ingredient-card"
              >
                <div class="ingredient-icon">
                  <el-icon><Opportunity /></el-icon>
                </div>
                <div>
                  <h4>{{ item.name }}</h4>
                  <p>{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="action-stack">
            <button class="primary-action" type="button">
              <el-icon><ChatDotRound /></el-icon>
              立即咨询
            </button>
            <button class="secondary-action" type="button">
              <el-icon><Service /></el-icon>
              联系经理
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Empty State -->
    <main v-else-if="!loading" class="detail-main">
      <el-empty description="产品不存在或已下架" />
    </main>

    <!-- Footer -->
    <footer class="detail-footer">
      <strong>CosmeticLab</strong>
      <div class="footer-links">
        <span>隐私政策</span>
        <span>服务条款</span>
        <span>LinkedIn</span>
        <span>Behance</span>
      </div>
      <span class="copyright">&copy; 2024 CosmeticLab 专业开发。保留所有权利。</span>
    </footer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  Calendar,
  ChatDotRound,
  Document,
  MagicStick,
  Opportunity,
  Picture,
  Service,
  Setting,
  SwitchButton,
  User,
} from '@element-plus/icons-vue'
import { productsApi } from '../../api/products'
import { useAuthStore } from '../../store/auth'

const props = defineProps({
  product: { type: Object, default: null },
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const fetchedProduct = ref(null)
const coverImage = ref('')
const currentImageIndex = ref(0)
const isGalleryHovered = ref(false)
let carouselTimer = null

const detailProduct = computed(() => props.product || fetchedProduct.value)

const galleryImages = computed(() => {
  const product = detailProduct.value
  if (!product) return []
  if (product.images?.length) return product.images
  const url = product.image_url || product.image
  return url ? [{ id: url, url }] : []
})

const previewSrcList = computed(() => galleryImages.value.map((image) => image.url).filter(Boolean))

const ingredientItems = computed(() => {
  const ingredients = detailProduct.value?.ingredients || ''
  if (!ingredients) return []
  // Split by common separators: comma, semicolon, Chinese comma
  const parts = ingredients.split(/[,;，；]/).map(s => s.trim()).filter(Boolean)
  return parts.map((part, idx) => {
    // Try to split "name: desc" or "name - desc" patterns
    const match = part.match(/^(.+?)\s*[:：\-—]\s*(.+)$/)
    if (match) {
      return { name: match[1].trim(), desc: match[2].trim() }
    }
    return { name: part, desc: '' }
  })
})

async function loadProduct() {
  if (props.product || !route.params.id) return
  loading.value = true
  try {
    const res = await productsApi.get(route.params.id)
    fetchedProduct.value = res.data
  } finally {
    loading.value = false
  }
}

function handleUserCommand(command) {
  if (command === 'manage') {
    router.push('/admin/products')
  } else if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

function selectImage(index) {
  if (index < 0 || index >= galleryImages.value.length) return
  currentImageIndex.value = index
  coverImage.value = galleryImages.value[index].url
}

function stopCarousel() {
  if (carouselTimer) {
    clearInterval(carouselTimer)
    carouselTimer = null
  }
}

function startCarousel() {
  stopCarousel()
  if (galleryImages.value.length <= 1) return
  carouselTimer = setInterval(() => {
    if (isGalleryHovered.value) return
    const nextIndex = (currentImageIndex.value + 1) % galleryImages.value.length
    selectImage(nextIndex)
  }, 3500)
}

watch(
  galleryImages,
  (images) => {
    if (!images.length) {
      currentImageIndex.value = 0
      coverImage.value = ''
      stopCarousel()
      return
    }
    const matchedIndex = images.findIndex((image) => image.url === coverImage.value)
    if (matchedIndex >= 0) {
      currentImageIndex.value = matchedIndex
    } else {
      selectImage(0)
    }
    startCarousel()
  },
  { immediate: true }
)

onMounted(loadProduct)
onBeforeUnmount(stopCarousel)
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  color: #191c1d;
  position: relative;
}

/* Background Gradient */
.detail-page::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: -1;
  background: linear-gradient(135deg, #ffffff 0%, #ffffff 60%, rgba(0, 51, 102, 0.03) 100%);
  pointer-events: none;
}

/* ===== Header ===== */
.detail-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(195, 198, 209, 0.2);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
  padding: 0 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-size: 24px;
  font-weight: 600;
  color: #003366;
  text-decoration: none;
  letter-spacing: -0.3px;
}

.avatar-btn {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border: 2px solid rgba(0, 51, 102, 0.1);
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s;
}

.avatar-btn:hover {
  border-color: #003366;
}

.avatar-btn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ===== Main ===== */
.detail-main {
  flex: 1;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  padding: 70px 64px 64px;
}

/* ===== Breadcrumbs ===== */
.crumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 12px;
  font-weight: 500;
  color: #43474f;
}

.crumbs a {
  color: #43474f;
  text-decoration: none;
  transition: color 0.15s;
}

.crumbs a:hover {
  color: #003366;
}

.crumbs .el-icon {
  font-size: 16px;
  color: #43474f;
}

.crumbs-current {
  color: #003366;
  font-weight: 600;
}

/* ===== Title Section (now inside info-col) ===== */
.title-section {
  margin-bottom: 0;
}

.title-section h1 {
  margin: 0;
  font-size: 36px;
  line-height: 44px;
  letter-spacing: -0.02em;
  font-weight: 700;
  color: #003366;
}

.title-sub {
  margin: 6px 0 0;
  font-size: 20px;
  line-height: 28px;
  font-weight: 400;
  color: #43474f;
}

/* ===== Split Layout ===== */
.split-layout {
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 48px;
  align-items: start;
}

/* ===== Gallery ===== */
.gallery-col {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.hero-image {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  background: #fff;
  box-shadow: 0 8px 32px rgba(0, 51, 102, 0.04);
  width: 100%;
  aspect-ratio: 4 / 5;
  max-height: clamp(420px, 52vh, 680px);
}

.hero-preview-image {
  width: 100%;
  height: 100%;
  display: block;
  cursor: zoom-in;
}

:deep(.hero-preview-image .el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.hero-image:hover :deep(.hero-preview-image .el-image__inner) {
  transform: scale(1.05);
}

.no-image {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #737780;
  background: #edeeef;
}

.thumb-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.thumb {
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 12px;
  border: 2px solid transparent;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.thumb.active {
  border-color: #003366;
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}

.thumb:not(.active) {
  opacity: 0.8;
  border: 1px solid rgba(195, 198, 209, 0.3);
}

.thumb:not(.active):hover {
  opacity: 1;
  border-color: rgba(0, 51, 102, 0.3);
}

.thumb img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.empty-thumb {
  display: grid;
  place-items: center;
  color: #737780;
  background: #edeeef;
}

/* ===== Info Column ===== */
.info-col {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow: visible;
}

/* Info Card */
.info-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  box-shadow: 0 8px 32px rgba(0, 51, 102, 0.04);
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
}

.date-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(237, 238, 239, 0.5);
  border: 1px solid rgba(195, 198, 209, 0.1);
  font-size: 14px;
  font-weight: 600;
  color: #43474f;
}

.date-badge .el-icon {
  font-size: 18px;
}

.tags-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tag-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-label {
  font-size: 12px;
  font-weight: 500;
  color: #737780;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

.tag-pill.form {
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  border: 1px solid rgba(0, 51, 102, 0.2);
}

.tag-pill.form:not(:first-child) {
  background: rgba(0, 51, 102, 0.05);
  color: rgba(0, 51, 102, 0.7);
  border: 1px solid rgba(0, 51, 102, 0.1);
}

.tag-pill.effect {
  background: #b1d5fe;
  color: #395c7f;
  border: 1px solid rgba(177, 213, 254, 0.5);
}

.tag-pill.function {
  background: #e1e3e4;
  color: #191c1d;
  border: 1px solid rgba(195, 198, 209, 0.3);
}

/* Section Block */
.section-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-heading {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  line-height: 32px;
  font-weight: 600;
  color: #003366;
}

.section-heading .el-icon {
  color: #3e6184;
  font-size: 22px;
}

.desc-text {
  margin: 0;
  font-size: 18px;
  line-height: 28px;
  color: #43474f;
}

/* Ingredients Grid */
.ingredients-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.ingredient-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  transition: border-color 0.15s;
}

.ingredient-card:hover {
  border-color: rgba(0, 51, 102, 0.3);
}

.ingredient-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  font-size: 18px;
  flex-shrink: 0;
}

.ingredient-card h4 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: #191c1d;
  line-height: 20px;
}

.ingredient-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #43474f;
}

/* Actions */
.action-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid rgba(195, 198, 209, 0.2);
}

.primary-action,
.secondary-action {
  height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.primary-action {
  border: 1px solid #003366;
  background: #003366;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.15);
}

.primary-action:hover {
  background: rgba(0, 51, 102, 0.9);
  box-shadow: 0 4px 12px rgba(0, 51, 102, 0.2);
}

.secondary-action {
  border: 2px solid #003366;
  background: transparent;
  color: #003366;
}

.secondary-action:hover {
  background: rgba(0, 51, 102, 0.05);
}

/* ===== Footer ===== */
.detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 40px 64px;
  border-top: 1px solid rgba(195, 198, 209, 0.2);
  background: #fff;
}

.detail-footer strong {
  font-size: 20px;
  font-weight: 600;
  color: #003366;
  letter-spacing: -0.3px;
}

.footer-links {
  display: flex;
  gap: 24px;
  color: #43474f;
  font-size: 12px;
  font-weight: 500;
}

.footer-links span {
  cursor: pointer;
  transition: color 0.15s;
}

.footer-links span:hover {
  color: #003366;
}

.copyright {
  font-size: 13px;
  color: #737780;
}

@media (min-width: 1600px) {
  .hero-image {
    max-height: clamp(520px, 60vh, 860px);
  }
}

/* ===== Responsive ===== */
@media (max-width: 1024px) {
  .split-layout {
    grid-template-columns: 1fr;
  }

  .hero-image {
    max-height: none;
  }

  :deep(.hero-preview-image .el-image__inner) {
    aspect-ratio: 16 / 9;
    height: auto;
  }

  .info-col {
    overflow-y: visible;
  }

  .ingredients-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 16px;
  }

  .detail-main {
    padding: 104px 16px 48px;
  }

  .title-section h1 {
    font-size: 32px;
    line-height: 40px;
  }

  .title-sub {
    font-size: 20px;
    line-height: 28px;
  }

  .split-layout {
    gap: 32px;
  }

  .thumb-row {
    grid-template-columns: repeat(4, 1fr);
  }

  .detail-footer {
    flex-direction: column;
    text-align: center;
    padding: 32px 16px;
  }

  .ingredients-grid {
    grid-template-columns: 1fr;
  }
}
</style>
