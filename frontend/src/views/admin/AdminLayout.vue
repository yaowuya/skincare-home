<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-top">
        <router-link class="brand" to="/">
          <span class="brand-icon">C</span>
          <span class="brand-text">CosmeticLab</span>
        </router-link>
      </div>
      <nav class="sidebar-nav">
        <router-link class="nav-item" to="/admin/products">
          <el-icon><Goods /></el-icon>
          <span>产品管理</span>
        </router-link>
        <router-link class="nav-item" to="/admin/tags">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </router-link>
        <router-link class="nav-item" to="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </router-link>
      </nav>
      <div class="sidebar-bottom">
        <el-dropdown trigger="click" @command="handleCommand" placement="right-end">
          <div class="user-trigger">
            <span class="user-avatar">{{ (authStore.user?.username || 'A').slice(0, 1).toUpperCase() }}</span>
            <span class="user-name">{{ authStore.user?.username || 'Admin' }}</span>
            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowRight, Goods, PriceTag, User } from '@element-plus/icons-vue'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f7f8fb;
  color: #1f2937;
}

/* ===== Sidebar ===== */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 10;
}

.sidebar-top {
  padding: 24px 20px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #111827;
}

.brand-icon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  background: #4350fe;
  color: #fff;
  font-size: 18px;
  font-weight: 800;
}

.brand-text {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.3px;
}

/* ===== Nav ===== */
.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  border-radius: 8px;
  color: #4b5563;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-item .el-icon {
  font-size: 18px;
}

.nav-item:hover {
  color: #4350fe;
  background: #f0f1ff;
}

.nav-item.router-link-active {
  color: #fff;
  background: #4350fe;
  box-shadow: 0 4px 12px rgba(67, 80, 254, 0.3);
}

.nav-item.router-link-active .el-icon {
  color: #fff;
}

/* ===== Bottom User ===== */
.sidebar-bottom {
  padding: 12px 10px 16px;
  border-top: 1px solid #f3f4f6;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.user-trigger:hover {
  background: #f9fafb;
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #dddfff;
  color: #4350fe;
  font-size: 13px;
  font-weight: 800;
}

.user-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  color: #9ca3af;
  font-size: 12px;
}

/* ===== Main Content ===== */
.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 32px 36px 56px;
  min-width: 0;
}

/* ===== Responsive ===== */
@media (max-width: 760px) {
  .sidebar {
    width: 60px;
  }
  .brand-text,
  .nav-item span,
  .user-name,
  .arrow-icon {
    display: none;
  }
  .brand {
    justify-content: center;
  }
  .nav-item {
    justify-content: center;
    padding: 0;
  }
  .sidebar-bottom {
    padding: 12px 6px 16px;
  }
  .user-trigger {
    justify-content: center;
    padding: 8px;
  }
  .main-content {
    margin-left: 60px;
    padding: 20px 16px 40px;
  }
}
</style>
