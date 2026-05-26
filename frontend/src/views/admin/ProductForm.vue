<template>
  <div class="product-form">
    <el-card shadow="never">
      <template #header>
        <span>{{ isEdit ? '编辑产品' : '新增产品' }}</span>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-loading="loading">
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
          <el-date-picker
            v-model="form.published_at"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
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
        <el-form-item v-if="isEdit" label="产品图片">
          <ImageUpload :product-id="productId" :current-images="currentImages" @change="onImagesChange" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">保 存</el-button>
          <el-button @click="$router.back()">取 消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTagsStore } from '../../store/tags'
import { productsApi } from '../../api/products'
import { ElMessage } from 'element-plus'
import ImageUpload from '../../components/ImageUpload.vue'

const route = useRoute()
const router = useRouter()
const tagsStore = useTagsStore()
const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const currentImages = ref([])

const productId = computed(() => route.params.id)
const isEdit = computed(() => !!productId.value)

const form = reactive({
  name: '',
  description: '',
  ingredients: '',
  published_at: '',
  form_type_ids: [],
  effect_type_ids: [],
  function_type_ids: [],
})

const rules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

function onImagesChange(images) {
  currentImages.value = images
}

async function loadProduct() {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await productsApi.get(productId.value)
    const p = res.data
    form.name = p.name
    form.description = p.description || ''
    form.ingredients = p.ingredients || ''
    form.published_at = p.published_at || ''
    form.form_type_ids = (p.form_tags || []).map((t) => t.id)
    form.effect_type_ids = (p.effect_tags || []).map((t) => t.id)
    form.function_type_ids = (p.function_tags || []).map((t) => t.id)
    currentImages.value = p.images || []
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await productsApi.update(productId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await productsApi.create(payload)
      ElMessage.success('创建成功')
    }
    router.push('/admin/products')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  tagsStore.fetchTags()
  loadProduct()
})
</script>
