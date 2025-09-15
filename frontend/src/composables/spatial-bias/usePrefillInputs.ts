import type { Ref } from 'vue'
import { auditExample } from '@/data/spatial-bias-examples/audit_input'
import { relabelExample } from '@/data/spatial-bias-examples/relabel_input'
import { thresholdExample } from '@/data/spatial-bias-examples/threshold_input'

export function usePrefillInputs(
  mode: Ref<'audit' | 'relabel' | 'threshold'>,
  indivInfoParsed: Ref<any[]>,
  indivInfoInput: Ref<string>,
  fitIndivParsed: Ref<any[]>,
  fitIndivInput: Ref<string>,
  predictIndivParsed: Ref<any[]>,
  predictIndivInput: Ref<string>,
  regionInfoParsed: Ref<any[]>,
  regionInfoInput: Ref<string>,
  predictRegionParsed: Ref<any[]>,
  predictRegionInput: Ref<string>
) {
  function prefillInputs() {
    if ((mode.value === 'audit') && indivInfoParsed.value.length === 0) {
      indivInfoParsed.value = auditExample.indiv
      indivInfoInput.value = JSON.stringify(auditExample.indiv.slice(0, 3), null, 2) + '\n...'

      regionInfoParsed.value = auditExample.region
      regionInfoInput.value = JSON.stringify(auditExample.region.slice(0, 2), null, 2) + '\n...'
    }

    if ((mode.value === 'relabel') && indivInfoParsed.value.length === 0) {
      indivInfoParsed.value = relabelExample.indiv
      indivInfoInput.value = JSON.stringify(relabelExample.indiv.slice(0, 3), null, 2) + '\n...'

      regionInfoParsed.value = relabelExample.region
      regionInfoInput.value = JSON.stringify(relabelExample.region.slice(0, 2), null, 2) + '\n...'
    }

    if (mode.value === 'threshold' && fitIndivParsed.value.length === 0) {
      fitIndivParsed.value = thresholdExample.fit_indiv
      fitIndivInput.value = JSON.stringify(thresholdExample.fit_indiv.slice(0, 3), null, 2) + '\n...'

      predictIndivParsed.value = thresholdExample.predict_indiv
      predictIndivInput.value = JSON.stringify(thresholdExample.predict_indiv.slice(0, 3), null, 2) + '\n...'

      predictRegionParsed.value = thresholdExample.predict_region
      predictRegionInput.value = JSON.stringify(thresholdExample.predict_region.slice(0, 2), null, 2) + '\n...'
    }
  }

  return { prefillInputs }
}
