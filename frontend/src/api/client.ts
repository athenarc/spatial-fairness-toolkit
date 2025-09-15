import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const IndivInfo = z.object({
  y_pred: z.number().int().gte(0).lte(1),
  lat: z.union([z.number(), z.null()]).optional(),
  lon: z.union([z.number(), z.null()]).optional(),
  y_true: z.union([z.number(), z.null()]).optional(),
  region_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
});
const RegionInfo = z
  .object({ polygon: z.union([z.array(z.array(z.number())), z.null()]) })
  .partial();
const AuditRequest = z.object({
  n_worlds: z.number().int().gte(1).lte(100000).optional().default(400),
  signif_level: z.number().gt(0).lt(1).optional().default(0.005),
  equal_opp: z.boolean().optional().default(true),
  indiv_info: z.array(IndivInfo).min(1),
  region_info: z.union([z.array(RegionInfo), z.null()]).optional(),
});
const StatEntry = z
  .object({
    idx: z.number().int(),
    stat: z.number(),
    is_signif: z.boolean().optional().default(false),
  })
  .passthrough();
const AuditResponse = z
  .object({
    sbi_score: z.number(),
    signif_thresh: z.number(),
    total_signif_regions: z.number().int(),
    fair_map_html: z.string(),
    fair_map_image: z.string(),
    stats: z.array(StatEntry),
    distribution_map_html: z.string(),
    distribution_map_image: z.string(),
  })
  .passthrough();
const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const RelabelingRequest = z.object({
  approx: z.boolean().optional().default(true),
  budget_constr: z.number().gte(0).lte(1).optional().default(0.2),
  pr_constr: z.number().gte(0).lte(1).optional().default(0.1),
  equal_opp: z.boolean().optional().default(true),
  n_worlds: z.number().int().gte(1).lte(100000).optional().default(400),
  signif_level: z.number().gt(0).lt(1).optional().default(0.005),
  work_limit: z.union([z.number(), z.null()]).optional().default(30),
  indiv_info: z.array(IndivInfo).min(1),
  region_info: z.union([z.array(RegionInfo), z.null()]).optional(),
});
const Metric = z.object({ name: z.string(), value: z.number() }).passthrough();
const MitigatedPredEntry = z
  .object({ idx: z.number().int(), y_pred: z.number().int() })
  .passthrough();
const RelabelingResponse = z
  .object({
    metrics_before: z.array(Metric),
    metrics_after: z.array(Metric),
    audit_before_mitigation: AuditResponse,
    audit_after_mitigation: AuditResponse,
    mitigated_preds: z.array(MitigatedPredEntry),
    flips_map_html: z.string(),
    flips_map_image: z.string(),
  })
  .passthrough();
const IndivInfoWithProbabilities = z.object({
  y_pred: z.number().int().gte(0).lte(1),
  lat: z.union([z.number(), z.null()]).optional(),
  lon: z.union([z.number(), z.null()]).optional(),
  y_true: z.union([z.number(), z.null()]).optional(),
  region_ids: z.union([z.array(z.number().int()), z.null()]).optional(),
  y_pred_prob: z.union([z.number(), z.null()]),
});
const ThresholdAdjustmentRequest = z.object({
  approx: z.boolean().optional().default(true),
  budget_constr: z.number().gte(0).lte(1).optional().default(0.2),
  pr_constr: z.number().gte(0).lte(1).optional().default(0.1),
  equal_opp: z.boolean().optional().default(true),
  n_worlds: z.number().int().gte(1).lte(100000).optional().default(400),
  signif_level: z.number().gt(0).lt(1).optional().default(0.005),
  work_limit: z.union([z.number(), z.null()]).optional().default(30),
  default_boundary: z.union([z.number(), z.null()]).optional().default(0.5),
  fit_indiv_info: z.array(IndivInfoWithProbabilities).min(1),
  predict_indiv_info: z.array(IndivInfoWithProbabilities).min(1),
  predict_region_info: z.union([z.array(RegionInfo), z.null()]).optional(),
});
const ThresholdEntry = z
  .object({
    idx: z.number().int(),
    threshold: z.number(),
    eq_to_thresh_flip_prob: z.number(),
  })
  .passthrough();
const ThresholdAdjustmentResponse = z
  .object({
    metrics_before: z.array(Metric),
    metrics_after: z.array(Metric),
    audit_before_mitigation: AuditResponse,
    audit_after_mitigation: AuditResponse,
    mitigated_preds: z.array(MitigatedPredEntry),
    threshold_chart_before: z.string(),
    threshold_chart_after: z.string(),
    new_thresholds: z.array(ThresholdEntry),
    flips_map_html: z.string(),
    flips_map_image: z.string(),
  })
  .passthrough();
const CorrelationRequest = z
  .object({
    include_pearson: z.boolean().default(true),
    include_spearman: z.boolean().default(true),
  })
  .partial()
  .passthrough();
const CorrelationResponse = z
  .object({
    dataset_shape: z.array(z.number().int()),
    feature_count: z.number().int(),
    pearson: z.union([z.record(z.record(z.number())), z.null()]).optional(),
    spearman: z.union([z.record(z.record(z.number())), z.null()]).optional(),
  })
  .passthrough();
const FeatureImportanceRequest = z.object({}).partial().passthrough();
const FeatureImportanceItem = z
  .object({ Feature: z.string(), Importance: z.number() })
  .passthrough();
const FeatureImportanceResponse = z
  .object({
    feature_importance: z.array(FeatureImportanceItem),
    model_names: z.array(z.string()),
    accuracy_scores: z.array(z.number()),
    best_model: z.string(),
    dataset_shape: z.array(z.number().int()),
  })
  .passthrough();

export const schemas = {
  IndivInfo,
  RegionInfo,
  AuditRequest,
  StatEntry,
  AuditResponse,
  ValidationError,
  HTTPValidationError,
  RelabelingRequest,
  Metric,
  MitigatedPredEntry,
  RelabelingResponse,
  IndivInfoWithProbabilities,
  ThresholdAdjustmentRequest,
  ThresholdEntry,
  ThresholdAdjustmentResponse,
  CorrelationRequest,
  CorrelationResponse,
  FeatureImportanceRequest,
  FeatureImportanceItem,
  FeatureImportanceResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/api/correlations/analyze",
    alias: "analyze_correlations_api_correlations_analyze_post",
    description: `Analyze feature correlations using Pearson and Spearman methods`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CorrelationRequest,
      },
    ],
    response: CorrelationResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/feature-importance/analyze",
    alias: "analyze_feature_importance_api_feature_importance_analyze_post",
    description: `Analyze feature importance using SHAP values`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
    ],
    response: FeatureImportanceResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/spatial-bias/audit",
    alias: "audit_endpoint_api_spatial_bias_audit_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AuditRequest,
      },
    ],
    response: AuditResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/spatial-bias/mitigate/relabel",
    alias: "relabel_endpoint_api_spatial_bias_mitigate_relabel_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RelabelingRequest,
      },
    ],
    response: RelabelingResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/spatial-bias/mitigate/threshold",
    alias:
      "threshold_adjustment_endpoint_api_spatial_bias_mitigate_threshold_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ThresholdAdjustmentRequest,
      },
    ],
    response: ThresholdAdjustmentResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const api = new Zodios("/api", endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
