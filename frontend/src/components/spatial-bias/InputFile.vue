<template>
  <div class="space-y-1">
    <label class="font-semibold block">{{ label }}</label>
    <div class="flex flex-col space-y-1">
      <input type="file" accept=".json" @change="handleFileUploadWrapper" />
      <div class="flex items-center space-x-4">
        <!-- <button
          @click="downloadSample(type, mode)"
          class="text-sm text-blue-600 underline hover:text-blue-800"
        >
          Download Example
        </button> -->
        <button @click="showFormat = true" class="text-sm underline text-blue-700 hover:text-black">
          View Example Format
        </button>
        <button @click="showExample = true" class="text-sm underline text-blue-600 hover:text-green-800">
          View Example
        </button>
      </div>
    </div>

    <!-- Example modal -->
    <SchemaModal
      v-if="showExample"
      :visible="showExample"
      :title="`Example Input for ${label}`"
      :content="getExample(mode, type)"
      @close="showExample = false"
    />

    <!-- Format modal -->
    <SchemaModal
      v-if="showFormat"
      :visible="showFormat"
      :title="`Format Schema for ${label}`"
      :content="getFormat(mode, type)"
      @close="showFormat = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SchemaModal from './SchemaModal.vue'

const props = defineProps<{
  label: string
  type: string
  mode: 'audit' | 'relabel' | 'threshold'
  handleFileUpload: (event: Event, type: string) => void
  downloadSample: (type: string, mode: 'audit' | 'relabel' | 'threshold') => void
}>()

const showExample = ref(false)
const showFormat = ref(false)

const handleFileUploadWrapper = (event: Event) => {
  props.handleFileUpload(event, props.type)
}

// ✅ View Example (actual content)
function getExample(mode: string, type: string): string {
  if (type === 'combined' && mode !== 'threshold') {
    return JSON.stringify({
      indiv_info: [{ y_pred: 1, y_true: 0, lat: 37.9, lon: 23.7, region_ids: [0]}],
      region_info: [{ polygon: [[37.9, 23.7], [37.8, 23.6], [37.7, 23.5]] }]
    }, null, 2)
  }

  if (type === 'combined' && (mode === 'threshold')) {
    return JSON.stringify({
      fit_indiv_info: [{ y_pred: 0, y_pred_prob: 0.2, lat: 37.9, lon: 23.7, y_true: 1, region_ids: [0] }],
      predict_indiv_info: [{ y_pred: 1, y_pred_prob: 0.7, lat: 37.8, lon: 23.6, y_true: 1, region_ids: [0] }],
      predict_region_info: [{ polygon: [[37.9, 23.7], [37.8, 23.6], [37.7, 23.5]] }]
    }, null, 2)
  }

  return '// No example available for this mode/type.'
}

// ✅ View Format (schema and types)
function getFormat(mode: string, type: string): string {
  if (type === 'combined' && mode !== 'threshold') {
    return `
{
  "indiv_info": [
    {
      "y_pred": int,
      "lat": float | null,
      "lon": float | null,
      "y_true": int | null,
      "region_ids": [int] | null
    }
  ],
  "region_info": [
    {
      "polygon": [[float, float]]
    }
  ]
}

  `
  }

  if (type === 'combined' && (mode === 'threshold')) {
    return `
{
  "fit_indiv_info": [
    {
      "y_pred": int,
      "y_pred_prob": float,
      "lat": float | null,
      "lon": float | null,
      "y_true": int | null,
      "region_ids": [int] | null
    }
  ],
  "predict_indiv_info": [
    {
      "y_pred": int,
      "y_pred_prob": float,
      "lat": float | null,
      "lon": float | null,
      "y_true": int | null,
      "region_ids": [int] | null
    }
  ],
  "predict_region_info": [
    {
      "polygon": [[float, float]]
    }
  ]
}
`
  }

  return '// No format available for this mode/type.'
}
</script>
