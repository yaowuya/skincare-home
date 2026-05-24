<template>
  <div class="product-list">
    <div class="page-header">
      <h2>产品管理</h2>
      <el-button type="primary" @click="$router.push('/admin/products/new')">
        <el-icon><Plus /></el-icon> 新增产品
      </el-button>
    </div>

    <el-card shadow="never">
      <div class="search-bar">
        <el-input
          v-model="store.filters.search"
          placeholder="搜索产品名称..."
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch" :icon="Search" />
          </template>
        </el-input>
      </div>

      <el-table :data="store.items" v-loading="store.loading" stripe>
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <el-image
              v-if="row.image_url"
              :src="row.image_url"
              :preview-src-list="[row.image_url]"
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 4px"
            />
            <div v-else class="no-image">无</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="剂型标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="t in (row.form_tags || [])" :key="t.id" size="small" type="primary" style="margin: 2px">{{ t.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="功效标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="t in (row.effect_tags || [])" :key="t.id" size="small" type="success" style="margin: 2px">{{ t.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="功能标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="t in (row.function_tags || [])" :key="t.id" size="small" type="warning" style="margin: 2px">{{ t.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布日期" width="120" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/admin/products/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确认删除此产品？" @confirm="store.deleteProduct(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="store.page"
          :total="store.total"
          :page-size="20"
          layout="total, prev, pager, next"
          @current-change="store.fetchProducts()"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useProductsStore } from '../../store/products'
import { Plus, Search } from '@element-plus/icons-vue'

const store = useProductsStore()

function handleSearch() {
  store.page = 1
  store.fetchProducts()
}

onMounted(() => {
  store.fetchProducts()
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
.search-bar {
  margin-bottom: 16px;
}
.pagination-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.no-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 12px;
}
</style>
