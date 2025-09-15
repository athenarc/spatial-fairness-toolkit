<template>
    <div class="mt-6">
      <h2 class="text-lg font-bold mb-2">Per-Region Audit Statistics</h2>
  
      <div class="text-sm mb-2">
        <p>Significance Threshold: <strong>{{ signifThresh?.toFixed(6) }}</strong></p>
        <p>Total Significant Regions: <strong>{{ totalSignifRegions }}</strong></p>
      </div>
  
      <div v-if="stats.length < fullStats.length" class="text-xs text-gray-600 italic mb-1">
        Showing first {{ stats.length }} of {{ fullStats.length }} regions.
      </div>
  
      <div class="overflow-x-auto max-h-[400px] border rounded">
        <table class="table-auto w-full text-sm">
          <thead class="bg-gray-100 sticky top-0">
            <tr>
              <th class="px-2 py-1 text-left">Region</th>
              <th class="px-2 py-1 text-left">SBI<sub>r</sub></th>
              <th class="px-2 py-1 text-left">Significant Bias?</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(stat, idx) in stats" :key="idx">
              <td class="px-2 py-1">{{ stat.idx }}</td>
              <td class="px-2 py-1">{{ stat.p_value.toFixed(6) }}</td>
              <td class="px-2 py-1">
                <span :class="stat.is_significant ? 'text-red-600 font-semibold' : 'text-gray-600'">
                  {{ stat.is_significant ? 'Yes' : 'No' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <button
        class="mt-3 px-4 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
        @click="$emit('download')"
      >
        Download CSV
      </button>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps<{
    stats: any[],
    fullStats: any[],
    signifThresh: number,
    totalSignifRegions: number,
    mode: 'audit' | 'relabel' | 'threshold'
  }>()
  
  defineEmits(['download'])
  </script>
  