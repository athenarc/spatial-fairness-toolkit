<!-- components/SchemaModal.vue -->
<template>
    <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-40 z-50 flex items-center justify-center">
      <div class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] p-6 relative overflow-y-auto">
        <button @click="close" class="absolute top-2 right-2 text-gray-500 hover:text-black">✕</button>
        <h2 class="text-xl font-bold mb-4">{{ title }}</h2>
  
        <!-- Make this scrollable if content is long -->
        <div class="max-h-[60vh] overflow-y-auto">
          <pre class="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap">
  {{ content }}
          </pre>
        </div>
      </div>
    </div>
  </template>
  
  
  <script setup lang="ts">
  const props = defineProps<{
    visible: boolean
    title: string
    content: string
  }>()
  
  const emit = defineEmits(['close'])
  
  function close() {
    emit('close')
  }
  </script>
  