<template>
    <div class="mt-6 space-y-4">
      <h2 class="text-lg font-bold">Per-Region Audit Statistics</h2>
      <p class="text-sm text-gray-600 mb-2">Below you can compare regional spatial bias indices before and after applying the mitigation.</p>
  
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Before Mitigation -->
        <div class="bg-white border rounded p-4 shadow">
          <h3 class="font-semibold mb-2">Before Mitigation</h3>
          <AuditStatsTables
            :stats="beforeStats"
            :fullStats="fullBeforeStats"
            :signifThresh="signifThreshBefore"
            :totalSignifRegions="totalSignifRegionsBefore"
            mode="relabel"
            @download="triggerDownloadBefore"
          />
        </div>
  
        <!-- After Mitigation -->
        <div class="bg-white border rounded p-4 shadow">
          <h3 class="font-semibold mb-2">After Mitigation</h3>
          <AuditStatsTables
            :stats="afterStats"
            :fullStats="fullAfterStats"
            :signifThresh="signifThreshAfter"
            :totalSignifRegions="totalSignifRegionsAfter"
            mode="relabel"
            @download="triggerDownloadAfter"
          />
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import AuditStatsTables from './AuditStatsTables.vue'
  
  defineProps<{
    beforeStats: any[],
    fullBeforeStats: any[],
    totalSignifRegionsBefore: number,
    afterStats: any[],
    fullAfterStats: any[],
    totalSignifRegionsAfter: number,
    signifThreshBefore: number
    signifThreshAfter: number,
  }>()
  
  const emit = defineEmits<{
    (e: 'downloadBefore'): void
    (e: 'downloadAfter'): void
  }>()

  function triggerDownloadBefore() {
    emit('downloadBefore')
  }

  function triggerDownloadAfter() {
    emit('downloadAfter')
  }

  </script>
  