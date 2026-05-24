# Frontend — Admin Pages

**Goal:** Build the admin SPA: login, layout with sidebar, dashboard, and CRUD pages for products/users/tags.

**Depends on:** `01-scaffold.md`

---

## Task F2.1: Admin login page

**File:** `frontend/src/views/admin/AdminLogin.vue`

```vue
<template>
  <div class="login-container">
    <el-card class="login-card" header="管理员登录">
      <el-form :model="form" @keyup.enter="handleLogin">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item><el-button type="primary" @click="handleLogin" :loading="loading" style="width:100%">登录</el-button></el-form-item>
      </el-form>
      <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
const store = useAuthStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''; loading.value = true
  try {
    await store.login(form.username, form.password)
    router.push('/admin/dashboard')
  } catch (e) {
    error.value = e.response?.data?.message || '登录失败'
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-container { display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f0f2f5; }
.login-card { width:400px; }
</style>
```

---

## Task F2.2: Admin layout (sidebar + header)

**File:** `frontend/src/views/admin/AdminLayout.vue`

Sidebar with primary color `#1a56a8`. Menu items: 仪表盘, 产品管理, 用户管理, 标签管理. Header shows username on right with logout dropdown. Collapse toggle button on header left. Uses `el-container`, `el-aside`, `el-header`, `el-main`. Router-view renders child routes in main area.

Key elements: `el-menu` with `router` prop, `el-dropdown` for logout, collapse state with `isCollapse` ref.

---

## Task F2.3: Dashboard page

**File:** `frontend/src/views/admin/Dashboard.vue`

Four stat cards in an `el-row` grid:
- 产品总数 (from `productsApi.list({per_page:1})` → `total`)
- 用户总数 (from `usersApi.list()` → array length)
- 待审核用户 (from `usersApi.list({approved:'false'})` → array length)
- 标签总数 (sum of all three tag types)

Fetch all four on `onMounted` via `Promise.all`.

---

## Task F2.4: Product list page

**File:** `frontend/src/views/admin/ProductList.vue`

Features:
- Header: title "产品管理" + "新增产品" button linking to `/admin/products/new`
- Search bar: `el-input` with clearable + search button, binds to `store.filters.search`
- `el-table` with columns: image thumbnail (50x50), name, form_tags (blue tags), effect_tags (green tags), function_tags (yellow tags), published_at, actions (edit + delete)
- Delete uses `el-popconfirm` for confirmation
- Pagination: `el-pagination` at bottom, `@current-change` calls `store.fetchProducts()`
- Uses `useProductsStore()`

---

## Task F2.5: Product form page

**File:** `frontend/src/views/admin/ProductForm.vue`

Handles both create and edit mode (detected by `route.params.id`). Form fields:
- 产品名称 (required, `el-input`)
- 描述 (`el-input type="textarea" rows=3`)
- 成分列表 (`el-input type="textarea" rows=3`, placeholder提示行分隔)
- 发布日期 (`el-date-picker` format YYYY-MM-DD)
- 剂型标签 (`el-select multiple`, options from `tags.formTags`)
- 功效标签 (`el-select multiple`, options from `tags.effectTags`)
- 功能标签 (`el-select multiple`, options from `tags.functionTags`)
- 产品图片 (`ImageUpload` component, see below)
- Save + Cancel buttons

On mount: `tags.fetchTags()` then if editing, `productsApi.get(id)` to populate form. On save: `POST` or `PUT` to API.

**ImageUpload component** (`frontend/src/components/ImageUpload.vue`):
- Shows current image thumbnail with click-to-replace
- Or shows upload button when no image
- Validates file type (jpg/png/webp) and size (<5MB)
- Uploads via `productsApi.uploadImage(productId, file)`
- Delete button removes image via `productsApi.deleteImage(productId)`

---

## Task F2.6: User list page

**File:** `frontend/src/views/admin/UserList.vue`

`el-table` columns: username, email, role (tag: admin=red, user=gray), is_approved (tag: approved=green, pending=yellow), created_at, actions.
Actions: "通过" button (green, only for pending users), "编辑" link to `/admin/users/:id/edit`, "删除" with popconfirm.

---

## Task F2.7: User form page

**File:** `frontend/src/views/admin/UserForm.vue`

Handles create + edit. Fields: username, email, password (in edit mode, placeholder "留空不修改" and not sent if empty), role (`el-select` with user/admin), is_approved (`el-switch` with active-text/inactive-text).

Edit mode: fetch user from `usersApi.list()` and find by ID match (since there's no GET single user endpoint).

> **优化建议：** 后端已提供 `GET /api/users/:id`，UserForm 编辑时可直接 `api.get('/users/' + id)` 获取单个用户数据。在 API 模块 `users.js` 中新增 `get: (id) => api.get('/users/' + id)` 即可。

---

## Task F2.8: Tag management page

**File:** `frontend/src/views/admin/TagManage.vue`

Three `el-card` columns in an `el-row` grid, one per tag type:
- 剂型分类 (form)
- 功效分类 (effect)
- 功能分类 (function)

Each card shows:
- Header: title + "新增" button (prompts via `ElMessageBox.prompt`)
- List of existing tags with edit (rename via prompt) and delete (popconfirm) buttons

---

## Task F2.9: Commit

```bash
git add frontend/src/views/admin/ frontend/src/components/
git commit -m "feat: add admin management pages"
```
