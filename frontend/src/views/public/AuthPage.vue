<template>
  <main class="auth-page">
    <section class="auth-visual" aria-hidden="true">
      <div class="visual-copy">
        <h1>形态之美，精准把握。</h1>
        <p>访问专业产品数据库，管理配方、功效与产品资产。</p>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-shell">
        <div class="brand-block">
          <h2>CosmeticLab</h2>
          <p>{{ isLogin ? '登录您的专业账号。' : '创建账号后等待管理员审核。' }}</p>
        </div>

        <div class="mode-tabs" role="tablist">
          <button :class="{ active: isLogin }" type="button" @click="switchMode('login')">登录</button>
          <button :class="{ active: !isLogin }" type="button" @click="switchMode('register')">注册</button>
        </div>

        <el-form
          ref="formRef"
          class="auth-form"
          :model="form"
          :rules="rules"
          :validate-on-rule-change="false"
          label-position="top"
          @submit.prevent="handleSubmit"
        >
          <el-form-item v-if="!isLogin" label="用户名" prop="username">
            <el-input v-model="form.username" :prefix-icon="User" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item v-else label="用户名" prop="username">
            <el-input v-model="form.username" :prefix-icon="User" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item v-if="!isLogin" label="邮箱" prop="email">
            <el-input v-model="form.email" :prefix-icon="Message" placeholder="name@example.com" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              :prefix-icon="Lock"
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
          <el-button class="submit-btn" type="primary" :loading="loading" native-type="submit">
            {{ isLogin ? '登录' : '创建账户' }}
          </el-button>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Message, User } from '@element-plus/icons-vue'
import { useAuthStore } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const mode = ref('login')

const isLogin = computed(() => mode.value === 'login')

const form = reactive({
  username: '',
  email: '',
  password: '',
})

const rules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: isLogin.value
    ? []
    : [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入有效邮箱', trigger: 'blur' },
      ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}))

async function switchMode(nextMode) {
  mode.value = nextMode
  await nextTick()
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (isLogin.value) {
      await authStore.login(form.username, form.password)
      ElMessage.success('登录成功')
      router.push(route.query.redirect || '/')
    } else {
      await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password,
      })
      ElMessage.success('注册成功，请等待管理员审核')
      await switchMode('login')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.error || (isLogin.value ? '登录失败' : '注册失败'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 1fr);
  background: #f8f9fa;
  color: #191c1d;
}
.auth-visual {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(0, 30, 64, 0.08), rgba(0, 30, 64, 0.7)),
    url('/imgs/微信图片_20260522151722_6287_33.jpg') center/cover;
}
.visual-copy {
  position: absolute;
  left: 64px;
  right: 64px;
  bottom: 64px;
  color: #fff;
}
.visual-copy h1 {
  margin: 0 0 12px;
  font-size: 44px;
  line-height: 1.18;
  font-weight: 700;
}
.visual-copy p {
  margin: 0;
  font-size: 17px;
  line-height: 1.7;
  opacity: 0.92;
}
.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 64px;
}
.auth-shell {
  width: 100%;
  max-width: 520px;
  padding: 40px;
  border: 1px solid rgba(195, 198, 209, 0.7);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 16px 32px rgba(0, 51, 102, 0.08);
  backdrop-filter: blur(16px);
}
.brand-block {
  margin-bottom: 28px;
}
.brand-block h2 {
  margin: 0 0 8px;
  color: #001e40;
  font-size: 34px;
  line-height: 1.2;
  font-weight: 700;
}
.brand-block p {
  margin: 0;
  color: #43474f;
  font-size: 15px;
}
.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 28px;
  border-bottom: 1px solid #d9dadb;
}
.mode-tabs button {
  height: 44px;
  border: 0;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: #43474f;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}
.mode-tabs button.active {
  border-color: #003366;
  color: #001e40;
}
.auth-form :deep(.el-form-item__label) {
  color: #191c1d;
  font-weight: 700;
}
.auth-form :deep(.el-input__wrapper) {
  min-height: 48px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #c3c6d1 inset;
}
.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #001e40 inset;
}
.submit-btn {
  width: 100%;
  height: 50px;
  margin-top: 8px;
  border-radius: 8px;
  background: #003366;
  border-color: #003366;
  font-weight: 700;
}
@media (max-width: 860px) {
  .auth-page {
    grid-template-columns: 1fr;
  }
  .auth-visual {
    display: none;
  }
  .auth-panel {
    min-height: 100vh;
    padding: 24px 16px;
  }
  .auth-shell {
    padding: 28px 20px;
  }
}
</style>
