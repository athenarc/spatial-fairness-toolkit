// src/composables/useDownloads.ts

import { computeAuditStats } from './useAuditStats'
import { auditExample } from '@/data/spatial-bias-examples/audit_input'
import { relabelExample } from '@/data/spatial-bias-examples/relabel_input'
import { thresholdExample } from '@/data/spatial-bias-examples/threshold_input'

function downloadBlob(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function downloadCSVFromJSON(filename: string, header: string[], rows: any[][]) {
  const csv = [header, ...rows].map(r => r.join(',')).join('\n')
  downloadBlob(csv, filename, 'text/csv')
}

function downloadJSONSample(filename: string, data: any) {
  downloadBlob(JSON.stringify(data, null, 2), filename, 'application/json')
}

function downloadSample(type: string, mode?: 'audit' | 'relabel' | 'threshold') {
  let content: any = {}

  if (type === 'combined') {
    if (mode === 'audit') {
      content = auditExample
    } else if (mode === 'relabel') {
      content = relabelExample
    } else if (mode === 'threshold') {
      content = thresholdExample
    }
  } else {
    // Optional: support legacy individual field-based downloads
    if (type === 'indiv') content = auditExample.indiv
    if (type === 'region') content = auditExample.region
    if (type === 'fit_indiv') content = thresholdExample.fit_indiv
    if (type === 'predict_indiv') content = thresholdExample.predict_indiv
    if (type === 'predict_region') content = thresholdExample.predict_region
  }

  const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${type}_sample.json`
  link.click()
}



function downloadAuditStatsCSV(results: any) {
  const stats = computeAuditStats(results)
  if (!stats.length) return

  const header = ['region_idx', 'p_value', 'is_significant']
  const rows = stats.map((stat: { idx: number; p_value: number; is_significant: boolean }) => [
    stat.idx,
    stat.p_value,
    stat.is_significant ? 'Yes' : 'No'
  ])
  downloadCSVFromJSON('audit_stats.csv', header, rows)
}

function downloadAuditStatsCSVVersion(results: any, label: 'before' | 'after') {
  const stats = computeAuditStats(
    label === 'before' ? results?.audit_before_mitigation : results?.audit_after_mitigation
  )
  if (!stats.length) return

  const header = ['region_idx', 'p_value', 'is_significant']
  const rows = stats.map((stat: { idx: number; p_value: number; is_significant: boolean }) => [
    stat.idx,
    stat.p_value,
    stat.is_significant ? 'Yes' : 'No'
  ])
  downloadCSVFromJSON(`audit_stats_${label}.csv`, header, rows)
}

function downloadThresholdCSV(results: any) {
  const data = results?.new_thresholds || []
  if (!data.length) return

  const header = ['idx', 'threshold', 'tie-braking probability']
  const rows = data.map((entry: { idx: number; threshold: number; eq_to_thresh_flip_prob: number, }) => [entry.idx, entry.threshold, entry.eq_to_thresh_flip_prob])
  downloadCSVFromJSON('new_thresholds.csv', header, rows)
}

function downloadMitigatedPredsCSV(results: any) {
  const data = results?.mitigated_preds || []
  if (!data.length) return

  const header = ['idx', 'y_pred']
  const rows = data.map((entry: { idx: number; y_pred: number }) => [entry.idx, entry.y_pred])
  downloadCSVFromJSON('mitigated_predictions.csv', header, rows)
}


export function useDownloads() {
  return {
    downloadCSVFromJSON,
    downloadJSONSample,
    downloadSample,
    downloadAuditStatsCSV,
    downloadAuditStatsCSVVersion,
    downloadThresholdCSV,
    downloadMitigatedPredsCSV
  }
}