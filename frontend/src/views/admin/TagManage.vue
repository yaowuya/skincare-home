<template>
  <div class="tag-manage">
    <h2 style="margin-top: 0">标签管理</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="group in tagGroups" :key="group.type">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ group.label }}</span>
              <el-button type="primary" size="small" @click="handleCreate(group.type)">新增</el-button>
            </div>
          </template>
          <div class="tag-list">
            <div v-for="tag in tagsStore.getTagsByType(group.type)" :key="tag.id" class="tag-item">
              <span class="tag-name">{{ tag.name }}</span>
              <div class="tag-actions">
                <el-button link type="primary" size="small" @click="handleEdit(group.type, tag)">编辑</el-button>
                <el-popconfirm title="确认删除此标签？" @confirm="tagsStore.deleteTag(group.type, tag.id)">
                  <template #reference>
                    <el-button link type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
            <el-empty v-if="tagsStore.getTagsByType(group.type).length === 0" description="暂无标签" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useTagsStore } from '../../store/tags'
import { ElMessageBox, ElMessage } from 'element-plus'

const tagsStore = useTagsStore()

const tagGroups = [
  { type: 'form', label: '剂型标签' },
  { type: 'effect', label: '功效标签' },
  { type: 'function', label: '功能标签' },
]

async function handleCreate(type) {
  try {
    const { value } = await ElMessageBox.prompt('请输入标签名称', '新增标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '标签名称不能为空',
    })
    await tagsStore.createTag(type, value.trim())
    ElMessage.success('创建成功')
  } catch {
    // cancelled
  }
}

async function handleEdit(type, tag) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新名称', '编辑标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: tag.name,
      inputPattern: /\S+/,
      inputErrorMessage: '标签名称不能为空',
    })
    await tagsStore.updateTag(type, tag.id, value.trim())
    ElMessage.success('更新成功')
  } catch {
    // cancelled
  }
}

onMounted(() => {
  tagsStore.fetchTags()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tag-list {
  max-height: 400px;
  overflow-y: auto;
}
.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.tag-item:last-child {
  border-bottom: none;
}
.tag-name {
  font-size: 14px;
  color: #303133;
}
.tag-actions {
  display: flex;
  gap: 4px;
}
</style>
