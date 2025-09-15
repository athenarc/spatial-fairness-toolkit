

<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Spatial Bias Tool</h1>

    <div>
      <label class="block font-semibold mb-1">Select Mode</label>
      <select v-model="mode" class="p-2 border rounded">
        <option value="audit">Audit</option>
        <option value="relabel">Mitigation (Relabeling)</option>
        <option value="threshold">Mitigation (Decision Boundaries Adjustment)</option>
      </select>
    </div> 

    <!-- <div v-if="mode === 'threshold'" class="space-y-6">
      <InputPanel :mode="mode" :handleFileUpload="handleFileUpload" :downloadSample="downloadSample" />
      <ConfigPanel :mode="mode" :advanced="advanced" />
    </div> -->


    <div class="space-y-6">
      <InputPanel :mode="mode" :handleFileUpload="handleFileUpload" :downloadSample="downloadSample" />
      <ConfigPanel :mode="mode" :advanced="advanced" />
    </div>

    <div v-if="loading" class="flex items-center space-x-2 text-blue-600 font-semibold">
      <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span>{{ loadingMessage }}</span>
    </div>


    <button
      @click="onRunAnalysis"
      :disabled="loading"
      class="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
    >
      {{ mode === 'audit' ? 'Perform Audit' : 'Perform Mitigation' }}
    </button>


    <ResultsPanel
      v-if="results"
      :mode="mode"
      :results="results"
      :downloadAuditStatsCSVVersion="downloadAuditStatsCSVVersion"
      :downloadAuditStatsCSV="() => downloadAuditStatsCSV(results)"
      :downloadThresholdCSV="() => downloadThresholdCSV(results)"
      :downloadMitigatedPredsCSV="() => downloadMitigatedPredsCSV(results)"
    />

    </div>
</template>

<script setup lang="ts">

  import { ref, computed, watch, onMounted } from 'vue'
  import ConfigPanel from '@/components/spatial-bias/ConfigPanel.vue'
  import InputPanel from '@/components/spatial-bias/InputPanel.vue'
  import ResultsPanel from '@/components/spatial-bias/ResultsPanel.vue'
  import { useDownloads } from '@/composables/spatial-bias/useDownloads'
  import { useSpatialBiasApi } from '@/composables/spatial-bias/useSpatialBiasApi'
  import { useFileUpload } from '@/composables/spatial-bias/useFileUpload'
  import { usePrefillInputs } from '@/composables/spatial-bias/usePrefillInputs'
  import { getAdvancedDefaults, type AdvancedUI } from '@/utils/spatialDefaults'


  const { runAnalysis } = useSpatialBiasApi()
  async function onRunAnalysis() {
    loading.value = true
    results.value = null
    try {
      const data = await runAnalysis({
        mode: mode.value,
        advanced: advanced.value,
        indivInfoParsed: indivInfoParsed.value,
        regionInfoParsed: regionInfoParsed.value,
        fitIndivParsed: fitIndivParsed.value,
        predictIndivParsed: predictIndivParsed.value,
        predictRegionParsed: predictRegionParsed.value,
      })
      results.value = data 
      console.log(mode.value, "results:", data)
    } catch (err: any) {
      // alert("Error running analysis: " + err.message)
        if (err.response?.data?.detail) {
          console.error('Validation errors:', err.response.data.detail)
          alert(
            "Validation Error:\n" +
              err.response.data.detail
                .map((e: any) => `${e.loc.join('.')} → ${e.msg}`)
                .join('\n')
          )
        } else {
          alert("Error running analysis: " + err.message)
        }
        alert("Error running analysis:\n" + (err?.message ?? String(err)))
    } finally {
      loading.value = false
    }
  }

  function toFullAdvanced(a: AdvancedUI) {
    return {
      equal_opp: a.equal_opp,
      signif_level: a.signif_level,
      n_worlds: a.n_worlds,
      budget_constr: a.budget_constr ?? 0.1,
      pr_constr: a.pr_constr ?? 0.1,
      approx: a.approx ?? true,
      wlimit: a.wlimit ?? 30,
      decision_bound: a.decision_bound ?? 0.5,
    }
  }

  const {
    downloadSample,
    downloadAuditStatsCSV,
    downloadAuditStatsCSVVersion,
    downloadThresholdCSV,
    downloadMitigatedPredsCSV
  } = useDownloads()

  const mode = ref<'audit' | 'relabel' | 'threshold'>('audit')

  // Input preview refs
  const indivInfoInput = ref('')
  const fitIndivInput = ref('')
  const predictIndivInput = ref('')
  const regionInfoInput = ref('')
  const predictRegionInput = ref('')

  // Parsed data refs
  const indivInfoParsed = ref<any[]>([])
  const fitIndivParsed = ref<any[]>([])
  const predictIndivParsed = ref<any[]>([])
  const regionInfoParsed = ref<any[]>([])
  const predictRegionParsed = ref<any[]>([])

  const loading = ref(false)

  // const advanced = ref({
  //   equal_opp: true,
  //   signif_level: 0.005,
  //   n_worlds: 1000,
  //   budget_constr: 0.2,
  //   pr_constr: 0.1,
  //   approx: true,
  //   wlimit: 30,
  //   decision_bound: 0.5
  // })

  // const advanced = ref<AdvancedUI>(getAdvancedDefaults(mode.value))

  // onMounted(() => {
  //   prefillInputs()
  //   advanced.value = getAdvancedDefaults(mode.value) // ensure backend defaults are applied
  //   prefillInputs()
  // })

  // watch(mode, () => {
  //   results.value = null
  //   advanced.value = getAdvancedDefaults(mode.value)
  //   prefillInputs()
  // })

  const advanced = ref(toFullAdvanced(getAdvancedDefaults(mode.value)))

  onMounted(() => {
    advanced.value = toFullAdvanced(getAdvancedDefaults(mode.value))
    prefillInputs()
  })

  watch(mode, () => {
    results.value = null
    advanced.value = toFullAdvanced(getAdvancedDefaults(mode.value))
    prefillInputs()
  })

  const results = ref<any>(null)

  const loadingMessage = computed(() => {
    if (mode.value === 'audit') return "Running spatial bias audit, please wait..."
    if (mode.value === 'relabel') return "Applying spatial bias mitigation, please wait..."
    if (mode.value === 'threshold') return "Applying spatial bias mitigation, please wait..."
    return "Running analysis, please wait..."
  })

  const { prefillInputs } = usePrefillInputs(
    mode,
    indivInfoParsed,
    indivInfoInput,
    fitIndivParsed,
    fitIndivInput,
    predictIndivParsed,
    predictIndivInput,
    regionInfoParsed,
    regionInfoInput,
    predictRegionParsed,
    predictRegionInput
  )

  const { handleFileUpload } = useFileUpload(
    mode,
    indivInfoParsed,
    indivInfoInput,
    fitIndivParsed,
    fitIndivInput,
    predictIndivParsed,
    predictIndivInput,
    regionInfoParsed,
    regionInfoInput,
    predictRegionParsed,
    predictRegionInput
  )


</script>

<style scoped>
iframe {
  background: white;
}
</style>
