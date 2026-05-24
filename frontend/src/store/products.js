import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { productsApi } from '../api/products'

export const useProductsStore = defineStore('products', () => {
  const items = ref([])
  const total = ref(0)
  const page = ref(1)
  const loading = ref(false)
  const filters = reactive({
    search: '',
    form_type_id: '',
    effect_type_id: '',
    function_type_id: '',
  })

  async function fetchProducts() {
    loading.value = true
    try {
      const res = await productsApi.list({ page: page.value, per_page: 20, ...filters })
      items.value = res.data.items
      total.value = res.data.total
      page.value = res.data.page
    } finally {
      loading.value = false
    }
  }

  async function deleteProduct(id) {
    await productsApi.delete(id)
    await fetchProducts()
  }

  return { items, total, page, loading, filters, fetchProducts, deleteProduct }
})
