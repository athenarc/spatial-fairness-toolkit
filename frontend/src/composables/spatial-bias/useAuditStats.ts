// src/composables/useAuditStats.ts
export function computeAuditStats(auditBlock: any) {
    const stats = auditBlock?.stats || []
    return stats.map((entry: any) => ({
      idx: entry.idx,
      p_value: entry.stat,
      is_significant: entry.is_signif,
    }))
  }
  