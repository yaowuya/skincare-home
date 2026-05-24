# Frontend — Vue 3 + Vite Scaffold

**Goal:** Initialize the Vue 3 project with Vite, Element Plus, Pinia, Vue Router, Axios interceptor, and core API/stores.

**Depends on:** Backend API plans (needs API contract but can be built independently).

---

## Task F1.1: Project scaffold

**Files:**  
- Create: `frontend/package.json`  
- Create: `frontend/vite.config.js`  
- Create: `frontend/index.html`  
- Create: `frontend/src/main.js`  
- Create: `frontend/src/App.vue`

### Step 1: `frontend/package.json`

```json
{
  "name": "skincare-home-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "pinia": "^3.0.0",
    "element-plus": "^2.9.0",
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "vite": "^6.3.0"
  }
}
```

### Step 2: `frontend/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { port: 3000, proxy: { '/api': 'http://localhost:5000', '/uploads': 'http://localhost:5000' } },
  build: { outDir: 'dist' },
})
```

### Step 3: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>CosmeticLab Insights</title></head>
<body><div id="app"></div><script type="module" src="/src/main.js"></script></body>
</html>
```

### Step 4: `frontend/src/main.js`

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
```

### Step 5: `frontend/src/App.vue`

```vue
<template><router-view /></template>
```

### Step 6: Install and build

```bash
cd frontend && npm install && npm run build
```

Expected: `frontend/dist/` created with `index.html` and `assets/`.

---

## Task F1.2: Axios instance + API modules

**Files:**  
- Create: `frontend/src/api/index.js`  
- Create: `frontend/src/api/auth.js`  
- Create: `frontend/src/api/products.js`  
- Create: `frontend/src/api/users.js`  
- Create: `frontend/src/api/tags.js`

### Step 1: `frontend/src/api/index.js` — Axios instance with JWT interceptor

```javascript
import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      if (window.location.pathname.startsWith('/admin') && !window.location.pathname.includes('/login')) {
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
```

### Step 2: API modules

**`frontend/src/api/auth.js`:**
```javascript
import api from './index'
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  changePassword: (data) => api.put('/auth/password', data),
}
```

**`frontend/src/api/products.js`:**
```javascript
import api from './index'
export const productsApi = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  uploadImage: (id, file) => { const fd = new FormData(); fd.append('image', file); return api.post(`/products/${id}/image`, fd); },
  deleteImage: (id) => api.delete(`/products/${id}/image`),
}
```

**`frontend/src/api/users.js`:**
```javascript
import api from './index'
export const usersApi = {
  list: (params) => api.get('/users', { params }),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  approve: (id, approved) => api.post(`/users/${id}/approve`, { approved }),
}
```

**`frontend/src/api/tags.js`:**
```javascript
import api from './index'
export const tagsApi = {
  list: (type) => api.get(`/tags/${type}`),
  create: (type, name) => api.post(`/tags/${type}`, { name }),
  update: (type, id, name) => api.put(`/tags/${type}/${id}`, { name }),
  delete: (type, id) => api.delete(`/tags/${type}/${id}`),
}
```

---

## Task F1.3: Pinia stores

**Files:**  
- Create: `frontend/src/store/auth.js`  
- Create: `frontend/src/store/products.js`  
- Create: `frontend/src/store/users.js`  
- Create: `frontend/src/store/tags.js`

### Step 1: `frontend/src/store/auth.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
  }

  function logout() {
    token.value = ''; user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, isAdmin, login, logout }
})
```

### Step 2: `frontend/src/store/products.js`

```javascript
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { productsApi } from '../api/products'

export const useProductsStore = defineStore('products', () => {
  const items = ref([])
  const total = ref(0); const page = ref(1); const loading = ref(false)
  const filters = reactive({ search: '', form_type_id: '', effect_type_id: '', function_type_id: '' })

  async function fetchProducts() {
    loading.value = true
    try {
      const res = await productsApi.list({ page: page.value, per_page: 20, ...filters })
      items.value = res.data.items; total.value = res.data.total; page.value = res.data.page
    } finally { loading.value = false }
  }

  return { items, total, page, loading, filters, fetchProducts }
})
```

### Step 3: `frontend/src/store/users.js`

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi } from '../api/users'

export const useUsersStore = defineStore('users', () => {
  const items = ref([]); const loading = ref(false)

  async function fetchUsers(params) {
    loading.value = true
    try { const res = await usersApi.list(params); items.value = res.data }
    finally { loading.value = false }
  }

  return { items, loading, fetchUsers }
})
```

### Step 4: `frontend/src/store/tags.js`

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '../api/tags'

export const useTagsStore = defineStore('tags', () => {
  const formTags = ref([]); const effectTags = ref([]); const functionTags = ref([])

  async function fetchTags() {
    const [form, effect, func] = await Promise.all([
      tagsApi.list('form'), tagsApi.list('effect'), tagsApi.list('function'),
    ])
    formTags.value = form.data; effectTags.value = effect.data; functionTags.value = func.data
  }

  function getTagsByType(type) {
    return { form: formTags, effect: effectTags, function: functionTags }[type]?.value || []
  }

  return { formTags, effectTags, functionTags, fetchTags, getTagsByType }
})
```

---

## Task F1.4: Router with guards

**Files:**  
- Create: `frontend/src/router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/public/Home.vue') },
  { path: '/products/:id', name: 'ProductDetail', component: () => import('../views/public/ProductDetail.vue') },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('../views/admin/AdminLogin.vue') },
  {
    path: '/admin', component: () => import('../views/admin/AdminLayout.vue'), redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/admin/Dashboard.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'products', name: 'ProductList', component: () => import('../views/admin/ProductList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'products/new', name: 'ProductNew', component: () => import('../views/admin/ProductForm.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'products/:id/edit', name: 'ProductEdit', component: () => import('../views/admin/ProductForm.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'users', name: 'UserList', component: () => import('../views/admin/UserList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'users/new', name: 'UserNew', component: () => import('../views/admin/UserForm.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'users/:id/edit', name: 'UserEdit', component: () => import('../views/admin/UserForm.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'tags', name: 'TagManage', component: () => import('../views/admin/TagManage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) return next('/admin/login')
    if (to.meta.requiresAdmin) {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user.role !== 'admin') return next('/')
    }
  }
  next()
})

export default router
```

---

## Task F1.5: Commit

```bash
git add frontend/
git commit -m "feat: add Vue 3 frontend scaffold with API modules and stores"
```
