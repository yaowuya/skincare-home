<template>
  <div class="image-upload">
    <div class="image-grid">
      <div v-for="image in images" :key="image.id || image.url" class="image-preview">
        <el-image :src="image.url" fit="cover" style="width: 148px; height: 148px; border-radius: 6px" />
        <div class="image-actions">
          <el-icon class="action-btn" @click="handleDelete(image)"><Delete /></el-icon>
        </div>
      </div>
      <el-upload
        :show-file-list="false"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        accept="image/jpeg,image/png,image/webp"
      >
        <div class="upload-trigger">
          <el-icon :size="28"><Plus /></el-icon>
          <div>上传图片</div>
        </div>
      </el-upload>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { productsApi } from '../api/products'
import { ElMessage } from 'element-plus'

const props = defineProps({
  productId: { type: [String, Number], required: true },
  currentImage: { type: String, default: '' },
  currentImages: { type: Array, default: () => [] },
})
const emit = defineEmits(['change'])

const images = computed(() => {
  if (props.currentImages.length) return props.currentImages
  if (!props.currentImage) return []
  return [{ id: props.currentImage, url: props.currentImage }]
})

function beforeUpload(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG/PNG/WebP 格式')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

async function handleUpload({ file }) {
  try {
    const res = await productsApi.uploadImage(props.productId, file)
    emit('change', [...images.value, res.data])
    ElMessage.success('上传成功')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '上传失败')
  }
}

async function handleDelete(image) {
  try {
    if (image.id && image.id !== image.url) {
      await productsApi.deleteSingleImage(props.productId, image.id)
      emit('change', images.value.filter((item) => item.id !== image.id))
    } else {
      await productsApi.deleteImage(props.productId)
      emit('change', [])
    }
    ElMessage.success('已删除')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '删除失败')
  }
}
</script>

<style scoped>
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.image-preview {
  position: relative;
  display: inline-block;
}
.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 0 6px 6px;
}
.action-btn {
  color: #fff;
  cursor: pointer;
  font-size: 16px;
}
.upload-trigger {
  width: 148px;
  height: 148px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  cursor: pointer;
  transition: border-color 0.3s;
}
.upload-trigger:hover {
  border-color: #1a56a8;
  color: #1a56a8;
}
</style>
