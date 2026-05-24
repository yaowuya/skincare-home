<template>
  <div class="user-list">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="$router.push('/admin/users/new')">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="store.items" v-loading="store.loading" stripe>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_approved ? 'success' : 'warning'" size="small">
              {{ row.is_approved ? '已通过' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_approved"
              size="small"
              type="success"
              @click="handleApprove(row.id, true)"
            >通过</el-button>
            <el-button
              v-if="row.is_approved"
              size="small"
              type="warning"
              @click="handleApprove(row.id, false)"
            >取消</el-button>
            <el-button size="small" @click="$router.push(`/admin/users/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确认删除此用户？" @confirm="store.deleteUser(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUsersStore } from '../../store/users'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useUsersStore()

async function handleApprove(id, approved) {
  try {
    await store.approveUser(id, approved)
    ElMessage.success(approved ? '已通过审核' : '已取消审核')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '操作失败')
  }
}

onMounted(() => {
  store.fetchUsers()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  color: #303133;
}
</style>
