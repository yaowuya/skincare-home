<template>
  <section class="admin-page">
    <div class="filter-card">
      <div class="filter-heading">
        <div>
          <h1>用户管理</h1>
          <p>管理系统用户信息及审核状态。</p>
        </div>
      </div>
      <div class="filter-controls">
        <el-input v-model="searchText" class="search-input" placeholder="搜索用户名或邮箱..." clearable size="large">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" class="filter-select" placeholder="全部状态" size="large">
          <el-option label="全部状态" value="all" />
          <el-option label="已通过" value="approved" />
          <el-option label="待审核" value="pending" />
        </el-select>
        <el-button type="primary" size="large" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>
    </div>

    <!-- 新增用户弹窗 -->
    <el-dialog v-model="showAddDialog" title="新增用户" width="580px" destroy-on-close @closed="resetAddForm">
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="80px" size="large">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="addForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="addForm.confirmPassword" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核通过">
          <el-switch v-model="addForm.is_approved" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取 消</el-button>
        <el-button type="primary" :loading="addSubmitting" @click="handleAddUser">保 存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑用户" width="580px" destroy-on-close @closed="resetEditForm">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px" size="large">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" type="password" show-password placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="editForm.confirmPassword" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" placeholder="请选择角色" style="width: 100%" disabled>
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核通过">
          <el-switch v-model="editForm.is_approved" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取 消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="handleEditUser">保 存</el-button>
      </template>
    </el-dialog>

    <div class="table-card">
      <el-table :data="pagedUsers" v-loading="store.loading" class="management-table">
        <el-table-column label="头像" width="90" align="center">
          <template #default="{ row }">
            <span class="user-avatar">{{ initialOf(row.username) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="用户名" min-width="200">
          <template #default="{ row }">
            <span class="user-name">{{ row.username }}</span>
            <span class="user-email">{{ row.email }}</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <span class="role-pill" :class="{ admin: row.role === 'admin' }">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="注册日期" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="审核状态" width="130">
          <template #default="{ row }">
            <span class="status-pill" :class="{ pending: !row.is_approved }">
              {{ row.is_approved ? '已通过' : '待审核' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <el-tooltip :content="row.is_approved ? '取消审核' : '审核通过'" placement="top">
                <button class="icon-action approve" type="button" @click="handleApprove(row.id, !row.is_approved)">
                  <el-icon><Check v-if="!row.is_approved" /><Close v-else /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="编辑用户" placement="top">
                <button class="icon-action edit" type="button" @click="openEditDialog(row)">
                  <el-icon><EditPen /></el-icon>
                </button>
              </el-tooltip>
              <el-popconfirm title="确认删除此用户？" @confirm="store.deleteUser(row.id)">
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
        <span>共 {{ filteredUsers.length }} 位用户</span>
        <el-pagination
          v-model:current-page="currentPage"
          :total="filteredUsers.length"
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
import { Check, Close, Delete, EditPen, Plus, Search } from '@element-plus/icons-vue'
import { useUsersStore } from '../../store/users'
import { usersApi } from '../../api/users'

const store = useUsersStore()
const searchText = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = 10

// ========== 新增用户弹窗 ==========
const showAddDialog = ref(false)
const addFormRef = ref(null)
const addSubmitting = ref(false)
const addForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'user',
  is_approved: false,
})

const validateAddConfirm = (_rule, value, callback) => {
  if (value !== addForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const addRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请再次输入密码', trigger: 'blur' }, { validator: validateAddConfirm, trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

function openAddDialog() {
  resetAddForm()
  showAddDialog.value = true
}

async function handleAddUser() {
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid) return
  addSubmitting.value = true
  try {
    const { confirmPassword, ...payload } = addForm
    await usersApi.create(payload)
    ElMessage.success('创建成功')
    showAddDialog.value = false
    store.fetchUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '创建失败')
  } finally {
    addSubmitting.value = false
  }
}

function resetAddForm() {
  addForm.username = ''
  addForm.email = ''
  addForm.password = ''
  addForm.confirmPassword = ''
  addForm.role = 'user'
  addForm.is_approved = false
}

// ========== 编辑用户弹窗 ==========
const showEditDialog = ref(false)
const editFormRef = ref(null)
const editSubmitting = ref(false)
const editingUserId = ref(null)
const editForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'user',
  is_approved: false,
})

const validateEditConfirm = (_rule, value, callback) => {
  if (!editForm.password && !value) {
    // 两个都为空 = 不修改密码，合法
    callback()
  } else if (value !== editForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const editRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
  password: [{ validator: (_r, v, cb) => { if (v && !editForm.confirmPassword) cb(new Error('请输入确认密码')); else cb() }, trigger: 'blur' }],
  confirmPassword: [{ validator: validateEditConfirm, trigger: 'blur' }],
}

async function openEditDialog(user) {
  editingUserId.value = user.id
  editForm.username = user.username || ''
  editForm.email = user.email || ''
  editForm.password = ''
  editForm.confirmPassword = ''
  editForm.role = user.role || 'user'
  editForm.is_approved = !!user.is_approved
  showEditDialog.value = true
}

async function handleEditUser() {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  editSubmitting.value = true
  try {
    const payload = { username: editForm.username, email: editForm.email, is_approved: editForm.is_approved }
    if (editForm.password) payload.password = editForm.password
    await usersApi.update(editingUserId.value, payload)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    store.fetchUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '更新失败')
  } finally {
    editSubmitting.value = false
  }
}

function resetEditForm() {
  editForm.username = ''
  editForm.email = ''
  editForm.password = ''
  editForm.confirmPassword = ''
  editForm.role = 'user'
  editForm.is_approved = false
  editingUserId.value = null
}

// ========== 列表筛选 ==========
const filteredUsers = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  return store.items.filter((user) => {
    const matchesKeyword = !keyword
      || String(user.username || '').toLowerCase().includes(keyword)
      || String(user.id || '').toLowerCase().includes(keyword)
      || String(user.email || '').toLowerCase().includes(keyword)
    const matchesStatus = statusFilter.value === 'all'
      || (statusFilter.value === 'approved' && user.is_approved)
      || (statusFilter.value === 'pending' && !user.is_approved)
    return matchesKeyword && matchesStatus
  })
})

const pagedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

watch([searchText, statusFilter], () => {
  currentPage.value = 1
})

async function handleApprove(id, approved) {
  try {
    await store.approveUser(id, approved)
    ElMessage.success(approved ? '已通过审核' : '已取消审核')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '操作失败')
  }
}

function initialOf(username = '') {
  return String(username || 'U').slice(0, 1).toUpperCase()
}

function formatDate(date) {
  if (!date) return '-'
  return String(date).slice(0, 10)
}

onMounted(() => {
  store.fetchUsers()
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
  width: 260px;
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
  height: 72px;
}
.user-avatar {
  width: 40px;
  height: 40px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  background: #dddfff;
  color: #4350fe;
  font-weight: 800;
}
.user-name {
  display: block;
  color: #111827;
  font-weight: 700;
}
.user-email {
  display: block;
  color: #6b7280;
  font-size: 12px;
  margin-top: 2px;
}
.role-pill,
.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 12px;
  font-weight: 800;
}
.role-pill.admin {
  background: #fee2e2;
  color: #991b1b;
}
.status-pill {
  background: #e8f7ef;
  color: #166534;
}
.status-pill.pending {
  background: #fff7ed;
  color: #c2410c;
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
.icon-action.approve {
  color: #166534;
}
.icon-action.approve:hover {
  background: #dcfce7;
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
