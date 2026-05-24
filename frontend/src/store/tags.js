import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '../api/tags'

export const useTagsStore = defineStore('tags', () => {
  const formTags = ref([])
  const effectTags = ref([])
  const functionTags = ref([])

  async function fetchTags() {
    const [form, effect, func] = await Promise.all([
      tagsApi.list('form'),
      tagsApi.list('effect'),
      tagsApi.list('function'),
    ])
    formTags.value = form.data
    effectTags.value = effect.data
    functionTags.value = func.data
  }

  async function createTag(type, name) {
    await tagsApi.create(type, name)
    await fetchTags()
  }

  async function updateTag(type, id, name) {
    await tagsApi.update(type, id, name)
    await fetchTags()
  }

  async function deleteTag(type, id) {
    await tagsApi.delete(type, id)
    await fetchTags()
  }

  function getTagsByType(type) {
    const map = { form: formTags, effect: effectTags, function: functionTags }
    return map[type]?.value || []
  }

  return { formTags, effectTags, functionTags, fetchTags, createTag, updateTag, deleteTag, getTagsByType }
})
