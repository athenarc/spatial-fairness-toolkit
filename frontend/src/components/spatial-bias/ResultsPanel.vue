<template>
    <div class="mt-8 space-y-6" v-if="results">
  
      <!-- 1. Metrics Comparison -->
      <div v-if="results.metrics_before || results.metrics_after">
        <h2 class="text-lg font-bold mb-2">Metrics Comparison</h2>
        <table class="table-auto border-collapse border border-gray-300">
          <thead class="bg-gray-100">
            <tr>
              <th class="border px-4 py-2 text-left">Metric</th>
              <th class="border px-4 py-2 text-left">Before</th>
              <th class="border px-4 py-2 text-left">After</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="metric in mergedMetrics" :key="metric.name">
              <td class="border px-4 py-2">{{ metric.name }}</td>
              <td class="border px-4 py-2">{{ formatMetric(metric.before) }}</td>
              <td class="border px-4 py-2">{{ formatMetric(metric.after) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- 2. Maps -->
      <div v-if="mode === 'audit'">
        <h2 class="text-lg font-bold mb-2">Audit Maps</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

          <div>
            <h3 class="font-semibold mb-1">Population Distribution</h3>
            <div v-if="results.distribution_map_image">
              <img :src="results.distribution_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.distribution_map_html" class="w-full h-[500px] border" />
          </div>

          <div>
            <h3 class="font-semibold mb-1">Identified Bias per Region</h3>
            <div v-if="results.fair_map_image">
              <img :src="results.fair_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.fair_map_html" class="w-full h-[500px] border" />

          </div>
        </div>
      </div>
  
      <div v-else>
        <h2 class="text-lg font-bold mb-2">Original Predictions and Mitigation Changes<span v-if="mode === 'threshold'"> - Test Set</span></h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-semibold mb-1">Population Distribution</h3>
            <div v-if="results.audit_before_mitigation?.distribution_map_image">
              <img :src="results.audit_before_mitigation?.distribution_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.audit_before_mitigation?.distribution_map_html" class="w-full h-[500px] border" />
          </div>
          <div>
            <h3 class="font-semibold mb-1">Prediction Changes (Flips)</h3>
            <div v-if="results.flips_map_image">
              <img :src="results.flips_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.flips_map_html" class="w-full h-[500px] border" />
          </div>
        </div>
  
        <h2 class="text-lg font-bold mb-2">Identified Bias per Region<span v-if="mode === 'threshold'"> - Test Set</span></h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-semibold mb-1">Base Model</h3>
            <div v-if="results.audit_before_mitigation?.fair_map_image">
              <img :src="results.audit_before_mitigation?.fair_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.audit_before_mitigation?.fair_map_html" class="w-full h-[500px] border" />
          </div>
          <div>
            <h3 class="font-semibold mb-1">Mitigated Model</h3>
            <div v-if="results.audit_after_mitigation?.fair_map_image">
              <img :src="results.audit_after_mitigation?.fair_map_image" class="w-full h-[500px] border object-contain" />
            </div>
            <iframe v-else :srcdoc="results.audit_after_mitigation?.fair_map_html" class="w-full h-[500px] border" />
          </div>
        </div>
      </div>
  
      <!-- 3. Threshold Plots -->
      <div v-if="mode === 'threshold'">
        <h2 class="text-lg font-bold mb-2">Per-Region Decision Thresholds</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-semibold mb-1">Base Model</h3>
            <img :src="results.threshold_chart_before" class="w-full h-[400px] border object-contain" />
          </div>
          <div>
            <h3 class="font-semibold mb-1">Mitigated Model</h3>
            <img :src="results.threshold_chart_after" class="w-full h-[400px] border object-contain" />
          </div>
        </div>
        <div class="bg-gray-50 border border-gray-300 rounded p-4 space-y-2 shadow-sm mt-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-bold">Adjusted Thresholds Per Region</h2>
            <button @click="downloadThresholdCSV" class="px-4 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded">Download CSV</button>
          </div>
          <p class="text-sm text-gray-600">This file contains the updated thresholds per region after mitigation.</p>
        </div>
      </div>
  
      <!-- 4. Region Bias Tables -->
      <AuditStatsTables
        v-if="mode === 'audit' && results"
        :stats="computeAuditStats(results)"
        :fullStats="computeAuditStats(results)"
        :signifThresh="results.signif_thresh"
        :totalSignifRegions="results.total_signif_regions"
        :mode="mode"
        @download="downloadAuditStatsCSV"
      />

      <MitigationStatsTables
        v-if="mode !== 'audit' && results"
        :beforeStats="computeAuditStats(results.audit_before_mitigation)"
        :fullBeforeStats="computeAuditStats(results.audit_before_mitigation)"
        :totalSignifRegionsBefore="results.audit_before_mitigation?.total_signif_regions"
        :afterStats="computeAuditStats(results.audit_after_mitigation)"
        :fullAfterStats="computeAuditStats(results.audit_after_mitigation)"
        :totalSignifRegionsAfter="results.audit_after_mitigation?.total_signif_regions"
        :signifThreshBefore="results.audit_before_mitigation?.signif_thresh"
        :signifThreshAfter="results.audit_after_mitigation?.signif_thresh"
        @downloadBefore="() => downloadAuditStatsCSVVersion(results, 'before')"
        @downloadAfter="() => downloadAuditStatsCSVVersion(results, 'after')"
      />

    
  
      <!-- 5. Mitigated Predictions -->
      <div v-if="mode !== 'audit'" class="mt-6 bg-gray-50 border border-gray-300 rounded p-4 space-y-2 shadow-sm">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold">Mitigated Predictions</h2>
          <button @click="downloadMitigatedPredsCSV" class="px-4 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded">
            Download CSV
          </button>
        </div>
        <p class="text-sm text-gray-600">This file includes the final miitigated predictions (with <code>y_pred</code>) for each individual.</p>
      </div>
    </div>
  </template>
  

<script setup lang="ts">
      import { computed } from 'vue'
      import AuditStatsTables from './AuditStatsTables.vue'
      import MitigationStatsTables from './MitigationStatsTables.vue'
      import { computeAuditStats } from '@/composables/spatial-bias/useAuditStats'


      const mergedMetrics = computed(() => {
      const before = props.results?.metrics_before || []
      const after = props.results?.metrics_after || []

      const metricsMap = new Map<string, { before: number | null, after: number | null }>()

      for (const m of before) {
        metricsMap.set(m.name, { before: m.value, after: null })
      }
      for (const m of after) {
        const existing = metricsMap.get(m.name)
        if (existing) {
          existing.after = m.value
        } else {
          metricsMap.set(m.name, { before: null, after: m.value })
        }
      }

      // SBI
      const sbiBefore = props.results?.audit_before_mitigation?.sbi_score ?? null
      const sbiAfter = props.results?.audit_after_mitigation?.sbi_score ?? null
      metricsMap.set('Spatial Bias Index (SBI)', { before: sbiBefore, after: sbiAfter })

      return Array.from(metricsMap.entries()).map(([name, vals]) => ({
        name,
        before: vals.before,
        after: vals.after,
      }))
    })

    function formatMetric(value: number | null): string {
      if (value === null) return '—'
      if (Math.abs(value) < 1e-3 && value !== 0) return value.toExponential(2)
      return value.toFixed(3)
    }

    
    const props = defineProps<{
      mode: 'audit' | 'relabel' | 'threshold'
      results: any
      downloadAuditStatsCSVVersion: (results: any, label: 'before' | 'after') => void
      downloadAuditStatsCSV: () => void
      downloadThresholdCSV: () => void
      downloadMitigatedPredsCSV: () => void
    }>()
</script>
  