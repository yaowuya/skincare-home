<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ backgroundColor: stat.color }">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import { Goods, User, CircleCheck, CollectionTag } from '@element-plus/icons-vue'
import api from '../../api'

const stats = ref([
  { label: '产品总数', value: 0, icon: shallowRef(Goods), color: '#1a56a8' },
  { label: '用户总数', value: 0, icon: shallowRef(User), color: '#67c23a' },
  { label: '待审核用户', value: 0, icon: shallowRef(CircleCheck), color: '#e6a23c' },
  { label: '标签总数', value: 0, icon: shallowRef(CollectionTag), color: '#f56c6c' },
])

onMounted(async () => {
  try {
    const [productsRes, usersRes, formRes, effectRes, funcRes] = await Promise.all([
      api.get('/products', { params: { per_page: 1 } }),
      api.get('/users'),
      api.get('/tags/form'),
      api.get('/tags/effect'),
      api.get('/tags/function'),
    ])
    stats.value[0].value = productsRes.data.total || 0
    stats.value[1].value = (usersRes.data || []).length
    stats.value[2].value = (usersRes.data || []).filter((u) => !u.is_approved).length
    stats.value[3].value = (formRes.data || []).length + (effectRes.data || []).length + (funcRes.data || []).length
  } catch {
    // silently ignore
  }
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 2px;
}
</style>
