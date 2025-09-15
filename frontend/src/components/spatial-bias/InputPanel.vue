<template>
    <div class="border border-gray-300 rounded p-4 space-y-6">
      <h3 class="text-lg font-semibold">Input Data</h3>
  
      <InputFile
        label="Input File (JSON)"
        type="combined"
        :mode="mode" 
        :downloadSample="downloadSample"
        :handleFileUpload="handleFileUpload"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import InputFile from './InputFile.vue'
  
  defineProps<{
    mode: 'audit' | 'relabel' | 'threshold',
    handleFileUpload: (event: Event, type: string) => void,
    downloadSample: (type: string) => void
  }>()
  </script>
  