<template>
  <div class="user-form">
    <el-card shadow="never">
      <template #header>
        <span>{{ isEdit ? '编辑用户' : '新增用户' }}</span>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? '留空则不修改' : '请输入密码'" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核通过">
          <el-switch v-model="form.is_approved" />
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
import { usersApi } from '../../api/users'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const userId = computed(() => route.params.id)
const isEdit = computed(() => !!userId.value)

const form = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_approved: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

async function loadUser() {
  if (!isEdit.value) return
  try {
    const res = await usersApi.get(userId.value)
    const u = res.data
    form.username = u.username
    form.email = u.email
    form.role = u.role
    form.is_approved = u.is_approved
  } catch {
    // silently ignore
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value && !payload.password) delete payload.password
    if (isEdit.value) {
      await usersApi.update(userId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await usersApi.create(payload)
      ElMessage.success('创建成功')
    }
    router.push('/admin/users')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadUser()
})
</script>
