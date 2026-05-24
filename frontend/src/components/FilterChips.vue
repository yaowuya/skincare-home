<template>
  <div class="filter-chips">
    <div v-for="group in groups" :key="group.key" class="filter-group">
      <span class="group-label">{{ group.label }}</span>
      <div class="chip-list">
        <button
          v-for="item in group.items"
          :key="item.id"
          class="chip"
          :class="{ active: selected[group.key] === item.id }"
          @click="toggleSelect(group.key, item.id)"
        >{{ item.name }}</button>
        <button
          class="chip"
          :class="{ active: !selected[group.key] }"
          @click="toggleSelect(group.key, '')"
        >全部</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  groups: { type: Array, default: () => [] },
})
const emit = defineEmits(['change'])

const selected = reactive({
  form_type_id: '',
  effect_type_id: '',
  function_type_id: '',
})

function toggleSelect(key, id) {
  selected[key] = id
  emit('change', { ...selected })
}

watch(
  () => props.groups,
  () => {
    // reset when groups change
  }
)
</script>

<style scoped>
.filter-group {
  margin-bottom: 12px;
}
.group-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-right: 12px;
  white-space: nowrap;
}
.chip-list {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  padding: 4px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 16px;
  background: #fff;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.chip:hover {
  border-color: #1a56a8;
  color: #1a56a8;
}
.chip.active {
  background: #1a56a8;
  border-color: #1a56a8;
  color: #fff;
}
</style>
