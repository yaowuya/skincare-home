<template>
  <section class="admin-page">
    <div class="filter-card">
      <div class="filter-heading">
        <div>
          <h1>产品管理</h1>
          <p>管理和维护您的产品目录，包括剂型和功效信息。</p>
        </div>
      </div>
      <div class="filter-controls">
        <el-input
          v-model="store.filters.search"
          class="search-input"
          placeholder="搜索产品名称..."
          clearable
          size="large"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="store.filters.form_type_id" class="filter-select" placeholder="所有剂型" clearable size="large" @change="handleSearch">
          <el-option label="所有剂型" value="" />
          <el-option v-for="tag in tagsStore.formTags" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
        <el-select v-model="store.filters.effect_type_id" class="filter-select" placeholder="所有功效" clearable size="large" @change="handleSearch">
          <el-option label="所有功效" value="" />
          <el-option v-for="tag in tagsStore.effectTags" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
        <el-select v-model="store.filters.function_type_id" class="filter-select" placeholder="所有功能" clearable size="large" @change="handleSearch">
          <el-option label="所有功能" value="" />
          <el-option v-for="tag in tagsStore.functionTags" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
        <el-button type="primary" size="large" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          添加产品
        </el-button>
      </div>
    </div>

    <!-- 新增产品弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增产品" width="720px" destroy-on-close @closed="resetForm">
      <el-steps :active="addStep" align-center class="add-steps">
        <el-step title="基本信息" />
        <el-step title="上传图片" />
        <el-step title="预览确认" />
      </el-steps>

      <!-- 步骤1：基本信息 -->
      <div v-show="addStep === 0">
        <el-form ref="addFormRef" :model="form" :rules="formRules" label-width="90px" size="large">
          <el-form-item label="产品名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入产品名称" />
          </el-form-item>
          <el-form-item label="产品描述" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
          </el-form-item>
          <el-form-item label="成分" prop="ingredients">
            <el-input v-model="form.ingredients" type="textarea" :rows="3" placeholder="请输入成分" />
          </el-form-item>
          <el-form-item label="发布日期" prop="published_at">
            <el-date-picker v-model="form.published_at" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="剂型标签">
            <el-select v-model="form.form_type_ids" multiple placeholder="选择剂型标签" style="width: 100%">
              <el-option v-for="t in tagsStore.formTags" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="功效标签">
            <el-select v-model="form.effect_type_ids" multiple placeholder="选择功效标签" style="width: 100%">
              <el-option v-for="t in tagsStore.effectTags" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="功能标签">
            <el-select v-model="form.function_type_ids" multiple placeholder="选择功能标签" style="width: 100%">
              <el-option v-for="t in tagsStore.functionTags" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2：上传图片 -->
      <div v-show="addStep === 1">
        <div class="step-upload">
          <ImageUpload v-if="addProductId" :product-id="addProductId" :current-images="currentImages" @change="onImagesChange" />
          <div v-else class="upload-placeholder">
            <el-icon :size="48"><Picture /></el-icon>
            <p>请先完成基本信息并保存</p>
          </div>
        </div>
      </div>

      <!-- 步骤3：预览 -->
      <div v-show="addStep === 2">
        <div class="preview-wrapper">
          <div class="preview-gallery">
            <div class="preview-main-img">
              <span v-if="previewCoverImage" class="preview-grade-badge">
                <el-icon><Medal /></el-icon>
                Clinical Grade
              </span>
              <img v-if="previewCoverImage" :src="previewCoverImage" :alt="form.name" />
              <div v-else class="preview-no-img">
                <el-icon :size="36"><Picture /></el-icon>
              </div>
            </div>
          </div>
          <div class="preview-info">
            <div class="preview-info-card">
              <div v-if="form.form_type_ids.length" class="preview-tag-group">
                <span class="preview-tag-label">剂型</span>
                <div class="preview-tag-list">
                  <span v-for="tag in previewFormTags" :key="tag.id" class="preview-tag-pill form">{{ tag.name }}</span>
                </div>
              </div>
              <div v-if="form.effect_type_ids.length" class="preview-tag-group">
                <span class="preview-tag-label">功效</span>
                <div class="preview-tag-list">
                  <span v-for="tag in previewEffectTags" :key="tag.id" class="preview-tag-pill effect">{{ tag.name }}</span>
                </div>
              </div>
              <div v-if="form.function_type_ids.length" class="preview-tag-group">
                <span class="preview-tag-label">功能</span>
                <div class="preview-tag-list">
                  <span v-for="tag in previewFunctionTags" :key="tag.id" class="preview-tag-pill function">{{ tag.name }}</span>
                </div>
              </div>
            </div>
            <div v-if="form.description" class="preview-section">
              <h3 class="preview-section-heading">产品描述</h3>
              <p class="preview-desc">{{ form.description }}</p>
            </div>
            <div v-if="form.ingredients" class="preview-section">
              <h3 class="preview-section-heading">核心成分</h3>
              <p class="preview-desc">{{ form.ingredients }}</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="step-footer">
          <el-button v-if="addStep > 0" @click="addStep--">上一步</el-button>
          <div class="step-footer-right">
            <template v-if="addStep === 0">
              <el-button @click="showAddDialog = false">取 消</el-button>
              <el-button type="default" :loading="submitting" @click="handleSaveOnly">保 存</el-button>
              <el-button type="primary" :loading="submitting" @click="handleSaveAndNext">下一步</el-button>
            </template>
            <template v-else-if="addStep === 1">
              <el-button type="primary" @click="addStep = 2">下一步</el-button>
            </template>
            <template v-else>
              <el-button type="primary" @click="finishAdd">完 成</el-button>
            </template>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑产品弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑产品" width="660px" destroy-on-close @closed="resetForm">
      <el-form ref="editFormRef" :model="form" :rules="formRules" label-width="90px" size="large" v-loading="editLoading">
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
        </el-form-item>
        <el-form-item label="成分" prop="ingredients">
          <el-input v-model="form.ingredients" type="textarea" :rows="3" placeholder="请输入成分" />
        </el-form-item>
        <el-form-item label="发布日期" prop="published_at">
          <el-date-picker v-model="form.published_at" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="剂型标签">
          <el-select v-model="form.form_type_ids" multiple placeholder="选择剂型标签" style="width: 100%">
            <el-option v-for="t in tagsStore.formTags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="功效标签">
          <el-select v-model="form.effect_type_ids" multiple placeholder="选择功效标签" style="width: 100%">
            <el-option v-for="t in tagsStore.effectTags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="功能标签">
          <el-select v-model="form.function_type_ids" multiple placeholder="选择功能标签" style="width: 100%">
            <el-option v-for="t in tagsStore.functionTags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品图片">
          <ImageUpload :product-id="editingProductId" :current-images="currentImages" @change="onImagesChange" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEditProduct">保 存</el-button>
      </template>
    </el-dialog>

    <!-- 预览产品弹窗 -->
    <el-dialog v-model="showPreviewDialog" title="产品详情预览" width="860px" destroy-on-close @closed="previewProduct = null">
      <div v-if="previewProduct" class="detail-preview">
        <div class="detail-preview-gallery">
          <div class="detail-preview-hero">
            <span class="detail-preview-badge">
              <el-icon><Medal /></el-icon>
              Clinical Grade
            </span>
            <img v-if="detailCoverImg" :src="detailCoverImg" :alt="previewProduct.name" />
            <div v-else class="detail-preview-noimg">
              <el-icon :size="48"><Picture /></el-icon>
            </div>
          </div>
          <div v-if="previewProduct.images?.length > 1" class="detail-preview-thumbs">
            <button
              v-for="(img, idx) in previewProduct.images"
              :key="img.id || img.url"
              class="detail-thumb"
              :class="{ active: img.url === detailCoverImg }"
              type="button"
              @click="detailCoverImg = img.url"
            >
              <img :src="img.url" :alt="`${previewProduct.name} ${idx + 1}`" />
            </button>
          </div>
        </div>
        <div class="detail-preview-info">
          <h2>{{ previewProduct.name }}</h2>
          <div v-if="previewProduct.published_at" class="detail-date">
            <el-icon><Calendar /></el-icon>
            <span>发布日期: {{ previewProduct.published_at }}</span>
          </div>
          <div class="detail-tags">
            <div v-if="previewProduct.form_tags?.length" class="detail-tag-group">
              <span class="detail-tag-label">剂型</span>
              <div class="detail-tag-list">
                <span v-for="tag in previewProduct.form_tags" :key="tag.id" class="detail-tag-pill form">{{ tag.name }}</span>
              </div>
            </div>
            <div v-if="previewProduct.effect_tags?.length" class="detail-tag-group">
              <span class="detail-tag-label">功效</span>
              <div class="detail-tag-list">
                <span v-for="tag in previewProduct.effect_tags" :key="tag.id" class="detail-tag-pill effect">{{ tag.name }}</span>
              </div>
            </div>
            <div v-if="previewProduct.function_tags?.length" class="detail-tag-group">
              <span class="detail-tag-label">功能</span>
              <div class="detail-tag-list">
                <span v-for="tag in previewProduct.function_tags" :key="tag.id" class="detail-tag-pill function">{{ tag.name }}</span>
              </div>
            </div>
          </div>
          <div v-if="previewProduct.description" class="detail-section">
            <h3>产品描述</h3>
            <p>{{ previewProduct.description }}</p>
          </div>
          <div v-if="previewProduct.ingredients" class="detail-section">
            <h3>核心成分</h3>
            <div class="detail-ingredients-grid">
              <div v-for="(item, idx) in previewIngredientItems" :key="idx" class="detail-ingredient-card">
                <div class="detail-ingredient-icon">
                  <el-icon><Opportunity /></el-icon>
                </div>
                <div>
                  <h4>{{ item.name }}</h4>
                  <p v-if="item.desc">{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showPreviewDialog = false">关 闭</el-button>
      </template>
    </el-dialog>

    <div class="table-card">
      <el-table :data="store.items" v-loading="store.loading" class="management-table">
        <el-table-column label="产品图片" width="120">
          <template #default="{ row }">
            <el-image v-if="coverOf(row)" :src="coverOf(row)" :preview-src-list="[coverOf(row)]" fit="cover" class="product-thumb" />
            <div v-else class="thumb-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="产品名称" min-width="220" show-overflow-tooltip />
        <el-table-column label="剂型" min-width="160">
          <template #default="{ row }">
            <div class="tag-stack">
              <span v-for="tag in row.form_tags || []" :key="tag.id" class="soft-tag blue">{{ tag.name }}</span>
              <span v-if="!(row.form_tags || []).length" class="empty-text">-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="功效" min-width="160">
          <template #default="{ row }">
            <div class="tag-stack">
              <span v-for="tag in row.effect_tags || []" :key="tag.id" class="soft-tag green">{{ tag.name }}</span>
              <span v-if="!(row.effect_tags || []).length" class="empty-text">-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="功能" min-width="160">
          <template #default="{ row }">
            <div class="tag-stack">
              <span v-for="tag in row.function_tags || []" :key="tag.id" class="soft-tag purple">{{ tag.name }}</span>
              <span v-if="!(row.function_tags || []).length" class="empty-text">-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布日期" width="140">
          <template #default="{ row }">{{ row.published_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <el-tooltip content="预览详情" placement="top">
                <button class="icon-action preview" type="button" @click="openPreviewDialog(row)">
                  <el-icon><View /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="编辑产品" placement="top">
                <button class="icon-action edit" type="button" @click="openEditDialog(row)">
                  <el-icon><EditPen /></el-icon>
                </button>
              </el-tooltip>
              <el-popconfirm title="确认删除此产品？" @confirm="store.deleteProduct(row.id)">
                <template #reference>
                  <button class="icon-action danger" type="button">
                    <el-icon><Delete /></el-icon>
                  </button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <span>共 {{ store.total }} 条产品信息</span>
        <el-pagination v-model:current-page="store.page" :total="store.total" :page-size="20" layout="prev, pager, next" @current-change="store.fetchProducts()" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Calendar, Delete, EditPen, Medal, Opportunity, Picture, Plus, Search, View } from '@element-plus/icons-vue'
import { useProductsStore } from '../../store/products'
import { useTagsStore } from '../../store/tags'
import { productsApi } from '../../api/products'
import { ElMessage } from 'element-plus'
import ImageUpload from '../../components/ImageUpload.vue'

const store = useProductsStore()
const tagsStore = useTagsStore()

function handleSearch() {
  store.page = 1
  store.fetchProducts()
}

function coverOf(product) {
  return product.images?.[0]?.url || product.image_url || product.image || ''
}

// ========== 弹窗通用 ==========
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)
const submitting = ref(false)
const editLoading = ref(false)
const editingProductId = ref(null)
const addProductId = ref(null)
const addStep = ref(0)
const currentImages = ref([])

const form = reactive({
  name: '',
  description: '',
  ingredients: '',
  published_at: '',
  form_type_ids: [],
  effect_type_ids: [],
  function_type_ids: [],
})

const formRules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

function resetForm() {
  form.name = ''
  form.description = ''
  form.ingredients = ''
  form.published_at = ''
  form.form_type_ids = []
  form.effect_type_ids = []
  form.function_type_ids = []
  currentImages.value = []
  editingProductId.value = null
  addProductId.value = null
  addStep.value = 0
}

function onImagesChange(images) {
  currentImages.value = images
}

function buildPayload() {
  const { form_type_ids, effect_type_ids, function_type_ids, ...baseFields } = form
  return {
    ...baseFields,
    form_tag_ids: form_type_ids,
    effect_tag_ids: effect_type_ids,
    function_tag_ids: function_type_ids,
  }
}

// ========== 新增产品 ==========
function openAddDialog() {
  resetForm()
  showAddDialog.value = true
}

async function doCreateProduct() {
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid) return false
  submitting.value = true
  try {
    const res = await productsApi.create(buildPayload())
    addProductId.value = res.data.id
    currentImages.value = []
    return true
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '创建失败')
    return false
  } finally {
    submitting.value = false
  }
}

// 仅保存，不跳步骤
async function handleSaveOnly() {
  if (!addProductId.value) {
    const ok = await doCreateProduct()
    if (!ok) return
    ElMessage.success('产品已创建')
  } else {
    // 已创建过，更新基本信息
    submitting.value = true
    try {
      await productsApi.update(addProductId.value, buildPayload())
      ElMessage.success('保存成功')
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '保存失败')
    } finally {
      submitting.value = false
    }
  }
}

// 保存并进入下一步（步骤1 → 步骤2）
async function handleSaveAndNext() {
  // 如果产品还没创建，先创建
  if (!addProductId.value) {
    const ok = await doCreateProduct()
    if (!ok) return
    ElMessage.success('产品已创建')
  }
  addStep.value = 1
}

function finishAdd() {
  showAddDialog.value = false
  store.fetchProducts()
}

// ========== 预览计算 ==========
const previewCoverImage = computed(() => currentImages.value?.[0]?.url || '')
const previewFormTags = computed(() =>
  form.form_type_ids.map((id) => tagsStore.formTags.find((x) => x.id === id)).filter(Boolean)
)
const previewEffectTags = computed(() =>
  form.effect_type_ids.map((id) => tagsStore.effectTags.find((x) => x.id === id)).filter(Boolean)
)
const previewFunctionTags = computed(() =>
  form.function_type_ids.map((id) => tagsStore.functionTags.find((x) => x.id === id)).filter(Boolean)
)

// ========== 编辑产品 ==========
async function openEditDialog(product) {
  resetForm()
  editingProductId.value = product.id
  showEditDialog.value = true
  editLoading.value = true
  try {
    const res = await productsApi.get(product.id)
    const p = res.data
    form.name = p.name
    form.description = p.description || ''
    form.ingredients = p.ingredients || ''
    form.published_at = p.published_at || ''
    form.form_type_ids = (p.form_tags || []).map((t) => t.id)
    form.effect_type_ids = (p.effect_tags || []).map((t) => t.id)
    form.function_type_ids = (p.function_tags || []).map((t) => t.id)
    currentImages.value = p.images || []
  } catch (err) {
    ElMessage.error('加载产品信息失败')
  } finally {
    editLoading.value = false
  }
}

async function handleEditProduct() {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await productsApi.update(editingProductId.value, buildPayload())
    ElMessage.success('更新成功')
    showEditDialog.value = false
    store.fetchProducts()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '更新失败')
  } finally {
    submitting.value = false
  }
}

// ========== 预览产品详情 ==========
const showPreviewDialog = ref(false)
const previewProduct = ref(null)
const detailCoverImg = ref('')

const previewIngredientItems = computed(() => {
  const ingredients = previewProduct.value?.ingredients || ''
  if (!ingredients) return []
  const parts = ingredients.split(/[,;，；]/).map(s => s.trim()).filter(Boolean)
  return parts.map((part) => {
    const match = part.match(/^(.+?)\s*[:：\-—]\s*(.+)$/)
    if (match) return { name: match[1].trim(), desc: match[2].trim() }
    return { name: part, desc: '' }
  })
})

async function openPreviewDialog(product) {
  try {
    const res = await productsApi.get(product.id)
    previewProduct.value = res.data
    detailCoverImg.value = res.data.images?.[0]?.url || res.data.image_url || res.data.image || ''
    showPreviewDialog.value = true
  } catch (err) {
    ElMessage.error('加载产品详情失败')
  }
}

onMounted(() => {
  tagsStore.fetchTags()
  store.fetchProducts()
})
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 24px;
}
.filter-card {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 18px;
}
.filter-heading h1 {
  margin: 0;
  color: #111827;
  font-size: 22px;
  line-height: 1.2;
  font-weight: 800;
}
.filter-heading p {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}
.filter-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.search-input {
  width: 220px;
}
.filter-select {
  width: 140px;
}
.filter-card,
.table-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(17, 24, 39, 0.04);
}
.table-card {
  overflow: hidden;
}
.management-table {
  width: 100%;
}
:deep(.management-table th.el-table__cell) {
  height: 54px;
  background: #f9fafb;
  color: #4b5563;
  font-weight: 800;
}
:deep(.management-table td.el-table__cell) {
  height: 76px;
}
.product-thumb,
.thumb-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 8px;
}
.thumb-placeholder {
  display: grid;
  place-items: center;
  background: #f3f4f6;
  color: #9ca3af;
}
.tag-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.soft-tag {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}
.soft-tag.blue {
  background: #f0f1ff;
  color: #4350fe;
}
.soft-tag.green {
  background: #e8f7ef;
  color: #166534;
}
.soft-tag.purple {
  background: #f0f1ff;
  color: #5b21b6;
}
.empty-text {
  color: #9ca3af;
}
.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
.icon-action {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
}
.icon-action.edit {
  color: #4350fe;
}
.icon-action.edit:hover {
  background: #f0f1ff;
}
.icon-action.preview {
  color: #003366;
}
.icon-action.preview:hover {
  background: #d5e3ff;
}
.icon-action.danger {
  color: #dc2626;
}
.icon-action.danger:hover {
  background: #fee2e2;
}
.table-footer {
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 18px;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 14px;
}

/* ===== Steps 步骤条 ===== */
.add-steps {
  margin-bottom: 24px;
}
.step-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.step-footer-right {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

/* ===== 上传步骤 ===== */
.step-upload {
  min-height: 200px;
}
.upload-placeholder {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #9ca3af;
}
.upload-placeholder p {
  margin: 0;
  font-size: 14px;
}

/* ===== 预览步骤 ===== */
.preview-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 28px;
  padding: 8px 0;
}
.preview-gallery {
  min-width: 0;
}
.preview-main-img {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  background: #f9fafb;
  box-shadow: 0 8px 32px rgba(0, 51, 102, 0.04);
}
.preview-main-img img {
  width: 100%;
  aspect-ratio: 4 / 5;
  display: block;
  object-fit: cover;
}
.preview-grade-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: #191c1d;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.preview-grade-badge .el-icon {
  color: #003366;
}
.preview-no-img {
  width: 100%;
  aspect-ratio: 4 / 5;
  display: grid;
  place-items: center;
  color: #c0c4cc;
}
.preview-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.preview-info-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.preview-tag-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.preview-tag-label {
  font-size: 12px;
  font-weight: 500;
  color: #737780;
}
.preview-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.preview-tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}
.preview-tag-pill.form {
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  border: 1px solid rgba(0, 51, 102, 0.2);
}
.preview-tag-pill.effect {
  background: #b1d5fe;
  color: #395c7f;
  border: 1px solid rgba(177, 213, 254, 0.5);
}
.preview-tag-pill.function {
  background: #e1e3e4;
  color: #191c1d;
  border: 1px solid rgba(195, 198, 209, 0.3);
}
.preview-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.preview-section-heading {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #003366;
}
.preview-desc {
  margin: 0;
  color: #43474f;
  font-size: 14px;
  line-height: 1.7;
}

@media (max-width: 900px) {
  .filter-card {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-controls {
    flex-wrap: wrap;
  }
  .search-input {
    width: 100%;
  }
  .preview-wrapper {
    grid-template-columns: 1fr;
  }
}

/* ===== 预览详情弹窗 ===== */
.detail-preview {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
}
.detail-preview-gallery {
  min-width: 0;
}
.detail-preview-hero {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  background: #f9fafb;
  box-shadow: 0 8px 32px rgba(0, 51, 102, 0.04);
}
.detail-preview-hero img {
  width: 100%;
  aspect-ratio: 4 / 5;
  display: block;
  object-fit: cover;
}
.detail-preview-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: #191c1d;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.detail-preview-badge .el-icon {
  color: #003366;
}
.detail-preview-noimg {
  width: 100%;
  aspect-ratio: 4 / 5;
  display: grid;
  place-items: center;
  color: #c0c4cc;
}
.detail-preview-thumbs {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-top: 12px;
}
.detail-thumb {
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  border: 2px solid transparent;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.15s;
}
.detail-thumb.active {
  border-color: #003366;
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}
.detail-thumb:not(.active) {
  opacity: 0.8;
  border: 1px solid rgba(195, 198, 209, 0.3);
}
.detail-thumb:not(.active):hover {
  opacity: 1;
}
.detail-thumb img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.detail-preview-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.detail-preview-info h2 {
  margin: 0;
  color: #003366;
  font-size: 24px;
  font-weight: 700;
}
.detail-date {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(237, 238, 239, 0.5);
  border: 1px solid rgba(195, 198, 209, 0.1);
  font-size: 13px;
  font-weight: 600;
  color: #43474f;
}
.detail-tags {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(195, 198, 209, 0.2);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.detail-tag-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.detail-tag-label {
  font-size: 12px;
  font-weight: 500;
  color: #737780;
}
.detail-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.detail-tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}
.detail-tag-pill.form {
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  border: 1px solid rgba(0, 51, 102, 0.2);
}
.detail-tag-pill.effect {
  background: #b1d5fe;
  color: #395c7f;
  border: 1px solid rgba(177, 213, 254, 0.5);
}
.detail-tag-pill.function {
  background: #e1e3e4;
  color: #191c1d;
  border: 1px solid rgba(195, 198, 209, 0.3);
}
.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.detail-section h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #003366;
}
.detail-section > p {
  margin: 0;
  color: #43474f;
  font-size: 14px;
  line-height: 1.7;
}
.detail-ingredients-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.detail-ingredient-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid rgba(195, 198, 209, 0.2);
}
.detail-ingredient-card:hover {
  border-color: rgba(0, 51, 102, 0.3);
}
.detail-ingredient-icon {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(0, 51, 102, 0.1);
  color: #003366;
  font-size: 14px;
  flex-shrink: 0;
}
.detail-ingredient-card h4 {
  margin: 0 0 2px;
  font-size: 13px;
  font-weight: 600;
  color: #191c1d;
}
.detail-ingredient-card p {
  margin: 0;
  font-size: 12px;
  color: #43474f;
  line-height: 1.4;
}

@media (max-width: 700px) {
  .detail-preview {
    grid-template-columns: 1fr;
  }
  .detail-ingredients-grid {
    grid-template-columns: 1fr;
  }
}
</style>
