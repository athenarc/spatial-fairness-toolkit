// src/utils/spatialDefaults.ts
import { schemas } from "@/api/client";

/**
 * UI-facing type (keeps your current prop names).
 * We map API names -> UI names where they differ (work_limit -> wlimit, default_boundary -> decision_bound).
 */
export type AdvancedUI = {
  equal_opp: boolean;
  signif_level: number;
  n_worlds: number;

  // Mitigation extras (visible in relabel & threshold modes):
  budget_constr?: number;
  pr_constr?: number;
  approx?: boolean;
  wlimit?: number;           // API: work_limit
  decision_bound?: number;   // API: default_boundary
};

/** Safely get a schema by name even if codegen used a slightly different name */
function pickRelabelSchema() {
  const anySchemas = schemas as any;
  return (
    anySchemas.RelabelingRequest ||
    anySchemas.RelabelRequest ||
    anySchemas.MitigationRelabelingRequest ||
    anySchemas.MitigationRequest // (fallback; will not have indiv_info keys anyway)
  );
}

export function getAdvancedDefaults(mode: "audit" | "relabel" | "threshold"): AdvancedUI {
  if (mode === "audit") {
    // Remove required array fields so we can parse {} and still get defaults.
    const s = schemas.AuditRequest.omit({ indiv_info: true, region_info: true });
    const d = s.parse({});
    return {
      equal_opp: d.equal_opp,
      signif_level: d.signif_level,
      n_worlds: d.n_worlds,
    };
  }

  if (mode === "relabel") {
    const RelabelSchema = pickRelabelSchema();
    // These may or may not exist on MitigationRequest; omit if present
    const s = RelabelSchema.omit?.({ indiv_info: true, region_info: true }) ?? RelabelSchema;
    const d = s.parse({});
    return {
      equal_opp: d.equal_opp,
      signif_level: d.signif_level,
      n_worlds: d.n_worlds,
      budget_constr: d.budget_constr,
      pr_constr: d.pr_constr,
      approx: d.approx,
      wlimit: d.work_limit ?? 30,
    };
  }

  // threshold
  const s = schemas.ThresholdAdjustmentRequest.omit({
    fit_indiv_info: true,
    predict_indiv_info: true,
    predict_region_info: true,
  });
  const d = s.parse({});
  return {
    equal_opp: d.equal_opp,
    signif_level: d.signif_level,
    n_worlds: d.n_worlds,
    budget_constr: d.budget_constr,
    pr_constr: d.pr_constr,
    approx: d.approx,
    wlimit: d.work_limit ?? 30,
    decision_bound: d.default_boundary ?? 0.5,
  };
}
