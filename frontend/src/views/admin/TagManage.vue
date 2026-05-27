<template>
  <section class="admin-page">
    <div class="filter-card">
      <div class="filter-heading">
        <div>
          <h1>标签管理</h1>
          <p>管理产品的剂型、功效和功能分类标签。</p>
        </div>
      </div>
      <div class="filter-controls">
        <el-select v-model="activeType" class="filter-select" size="large" @change="currentPage = 1">
          <el-option label="剂型标签" value="form" />
          <el-option label="功效标签" value="effect" />
          <el-option label="功能标签" value="function" />
        </el-select>
        <el-input v-model="searchText" class="search-input" placeholder="搜索标签名称..." clearable size="large">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增标签
        </el-button>
      </div>
    </div>

    <!-- 新增标签弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增标签" width="500px" destroy-on-close @closed="resetForm">
      <el-form ref="addFormRef" :model="form" :rules="formRules" label-width="80px" size="large">
        <el-form-item label="标签类型">
          <el-select v-model="form.type" style="width: 100%" disabled>
            <el-option label="剂型" value="form" />
            <el-option label="功效" value="effect" />
            <el-option label="功能" value="function" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" @keyup.enter="handleAdd" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAdd">保 存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑标签弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑标签" width="500px" destroy-on-close @closed="resetForm">
      <el-form ref="editFormRef" :model="form" :rules="formRules" label-width="80px" size="large">
        <el-form-item label="标签类型">
          <el-select v-model="form.type" style="width: 100%" disabled>
            <el-option label="剂型" value="form" />
            <el-option label="功效" value="effect" />
            <el-option label="功能" value="function" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" @keyup.enter="handleEdit" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEdit">保 存</el-button>
      </template>
    </el-dialog>

    <div class="table-card">
      <el-table :data="pagedTags" v-loading="tagsStore.loading" class="management-table">
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="标签名称" min-width="300">
          <template #default="{ row }">
            <span class="tag-pill" :class="activeType">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <el-tooltip content="编辑标签" placement="top">
                <button class="icon-action edit" type="button" @click="openEditDialog(row)">
                  <el-icon><EditPen /></el-icon>
                </button>
              </el-tooltip>
              <el-popconfirm title="确认删除此标签？" @confirm="handleDelete(row.id)">
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
        <span>共 {{ filteredTags.length }} 个标签</span>
        <el-pagination
          v-model:current-page="currentPage"
          :total="filteredTags.length"
          :page-size="pageSize"
          layout="prev, pager, next"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, EditPen, Plus, Search } from '@element-plus/icons-vue'
import { useTagsStore } from '../../store/tags'

const tagsStore = useTagsStore()

const activeType = ref('form')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = 20

// ========== 弹窗 ==========
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)
const submitting = ref(false)
const editingTagId = ref(null)

const form = reactive({
  type: 'form',
  name: '',
})

const formRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
}

function resetForm() {
  form.type = 'form'
  form.name = ''
  editingTagId.value = null
}

// ========== 列表数据 ==========
const filteredTags = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  const list = tagsStore.getTagsByType(activeType.value)
  if (!keyword) return list
  return list.filter((t) => String(t.name || '').toLowerCase().includes(keyword))
})

const pagedTags = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredTags.value.slice(start, start + pageSize)
})

watch([searchText, activeType], () => {
  currentPage.value = 1
})

// ========== 新增 ==========
function openAddDialog() {
  form.type = activeType.value
  form.name = ''
  showAddDialog.value = true
}

async function handleAdd() {
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await tagsStore.createTag(form.type, form.name.trim())
    ElMessage.success('创建成功')
    showAddDialog.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '创建失败')
  } finally {
    submitting.value = false
  }
}

// ========== 编辑 ==========
function openEditDialog(tag) {
  editingTagId.value = tag.id
  form.type = activeType.value
  form.name = tag.name
  showEditDialog.value = true
}

async function handleEdit() {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await tagsStore.updateTag(form.type, editingTagId.value, form.name.trim())
    ElMessage.success('更新成功')
    showEditDialog.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '更新失败')
  } finally {
    submitting.value = false
  }
}

// ========== 删除 ==========
async function handleDelete(id) {
  try {
    await tagsStore.deleteTag(activeType.value, id)
    ElMessage.success('删除成功')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '删除失败')
  }
}

onMounted(() => {
  tagsStore.fetchTags()
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
:deep(.management-table th.el-table__cell) {
  height: 54px;
  background: #f9fafb;
  color: #4b5563;
  font-weight: 800;
}
:deep(.management-table td.el-table__cell) {
  height: 56px;
}
.tag-pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}
.tag-pill.form {
  background: #f0f1ff;
  color: #4350fe;
}
.tag-pill.effect {
  background: #e8f7ef;
  color: #166534;
}
.tag-pill.function {
  background: #faf5ff;
  color: #5b21b6;
}
.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
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
}
</style>
