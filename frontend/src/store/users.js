import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi } from '../api/users'

export const useUsersStore = defineStore('users', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchUsers(params) {
    loading.value = true
    try {
      const res = await usersApi.list(params)
      items.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function deleteUser(id) {
    await usersApi.delete(id)
    await fetchUsers()
  }

  async function approveUser(id, approved) {
    const res = await usersApi.approve(id, approved)
    const idx = items.value.findIndex((u) => u.id === id)
    if (idx >= 0) items.value[idx] = res.data
  }

  return { items, loading, fetchUsers, deleteUser, approveUser }
})
