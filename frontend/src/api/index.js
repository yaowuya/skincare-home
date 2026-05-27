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
      // 避免在 /login 页面重复跳转
      if (window.location.pathname !== '/login') {
        // 延迟跳转，让当前请求的 catch 逻辑先执行
        setTimeout(() => {
          const redirect = encodeURIComponent(`${window.location.pathname}${window.location.search}`)
          window.location.href = `/login?redirect=${redirect}`
        }, 100)
      }
    }
    return Promise.reject(err)
  }
)

export default api
