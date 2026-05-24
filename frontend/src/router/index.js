import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/public/Home.vue'),
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('../views/public/ProductDetail.vue'),
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/AdminLogin.vue'),
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    redirect: '/admin/dashboard',
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
