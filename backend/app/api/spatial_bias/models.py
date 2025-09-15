# src/api/models.py

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, model_validator


class IndivInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")  # catch unknown keys

    y_pred: int = Field(..., ge=0, le=1)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    y_true: Optional[int] = Field(None, ge=0, le=1)
    region_ids: Optional[List[int]] = None

    @model_validator(mode="after")
    def _validate_indiv(self):
        # lat/lon must be provided together or not at all
        if (self.lat is None) ^ (self.lon is None):
            raise ValueError("lat and lon must be provided together")

        # region_ids (if present) must be a non-empty list of non-negative ints
        if self.region_ids is not None:
            if len(self.region_ids) == 0:
                raise ValueError("region_ids cannot be empty when provided")
            if any(
                r is None or not isinstance(r, int) or r < 0 for r in self.region_ids
            ):
                raise ValueError("region_ids must be non-negative integers")
        return self


class IndivInfoWithProbabilities(IndivInfo):
    y_pred_prob: Optional[float]


class RegionInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # polygon is list of [lat, lon]
    polygon: Optional[List[List[float]]] = None

    @model_validator(mode="after")
    def _validate_polygon(self):
        if self.polygon is None:
            return self
        if len(self.polygon) < 3:
            raise ValueError("polygon must have at least 3 points")
        for pt in self.polygon:
            if not isinstance(pt, list) or len(pt) != 2:
                raise ValueError("each polygon point must be [lat, lon]")
            # lat, lon = pt
            lon, lat = pt
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("polygon coordinates out of bounds")
        return self


class AuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    n_worlds: int = Field(400, ge=1, le=100_000)
    signif_level: float = Field(0.005, gt=0, lt=1)
    equal_opp: bool = True
    indiv_info: List[IndivInfo] = Field(..., min_length=1)
    region_info: Optional[List[RegionInfo]] = None

    @model_validator(mode="after")
    def _cross_field(self):
        # equal_opp => all have y_true
        if self.equal_opp:
            missing = [i for i, d in enumerate(self.indiv_info) if d.y_true is None]
            if missing:
                raise ValueError(
                    f"equal_opp=true requires y_true for all individuals (missing at indices {missing[:10]}...)"
                )

        have_coords = all(
            d.lat is not None and d.lon is not None for d in self.indiv_info
        )
        have_region_ids = all(
            d.region_ids is not None and len(d.region_ids) > 0 for d in self.indiv_info
        )

        if not have_coords and not have_region_ids:
            raise ValueError(
                "Provide either (lat+lon) for all individuals or region_ids for all individuals."
            )

        # If region_ids are used, region_info must exist & indices must be in range
        if have_region_ids and self.region_info is not None:
            # if not self.region_info or len(self.region_info) == 0:
            #     raise ValueError("region_ids provided but region_info is empty or missing.")
            max_idx = len(self.region_info) - 1
            bad = []
            for i, d in enumerate(self.indiv_info):
                for r in d.region_ids or []:
                    if r < 0 or r > max_idx:
                        bad.append((i, r))
            if bad:
                sample = ", ".join(f"(indiv {i}, region {r})" for i, r in bad[:10])
                raise ValueError(f"region_ids reference out-of-range indices: {sample}")
        return self


class MitigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approx: bool = True
    budget_constr: float = Field(0.2, ge=0.0, le=1.0)
    pr_constr: float = Field(0.1, ge=0.0, le=1.0)
    equal_opp: bool = True
    n_worlds: int = Field(400, ge=1, le=100_000)
    signif_level: float = Field(0.005, gt=0, lt=1)
    work_limit: Optional[int] = Field(30, ge=1)


class RelabelingRequest(MitigationRequest):
    indiv_info: List[IndivInfo] = Field(..., min_length=1)
    region_info: Optional[List[RegionInfo]] = None

    @model_validator(mode="after")
    def _cross_field(self):
        # reuse AuditRequest logic for indiv/region checks
        AuditRequest(
            n_worlds=self.n_worlds,
            signif_level=self.signif_level,
            equal_opp=self.equal_opp,
            indiv_info=self.indiv_info,
            region_info=self.region_info,
        )
        return self


class ThresholdAdjustmentRequest(MitigationRequest):
    default_boundary: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    fit_indiv_info: List[IndivInfoWithProbabilities] = Field(..., min_length=1)
    predict_indiv_info: List[IndivInfoWithProbabilities] = Field(..., min_length=1)
    predict_region_info: Optional[List[RegionInfo]] = None

    @model_validator(mode="after")
    def _cross_field(self):
        # probs required in threshold mode
        for group_name, group in (
            ("fit_indiv_info", self.fit_indiv_info),
            ("predict_indiv_info", self.predict_indiv_info),
        ):
            missing_prob = [i for i, d in enumerate(group) if d.y_pred_prob is None]
            if missing_prob:
                raise ValueError(
                    f"{group_name} requires y_pred_prob for all individuals (missing at indices {missing_prob[:10]}...)"
                )

        # equal_opp => y_true everywhere (both groups)
        if self.equal_opp:
            for group_name, group in (
                ("fit_indiv_info", self.fit_indiv_info),
                ("predict_indiv_info", self.predict_indiv_info),
            ):
                missing_ytrue = [i for i, d in enumerate(group) if d.y_true is None]
                if missing_ytrue:
                    raise ValueError(
                        f"equal_opp=true requires y_true in {group_name} (missing at indices {missing_ytrue[:10]}...)"
                    )

        # spatial requirements (predict set drives mapping/plots)
        have_coords_pred = all(
            d.lat is not None and d.lon is not None for d in self.predict_indiv_info
        )
        have_region_ids_pred = all(
            d.region_ids is not None and len(d.region_ids) > 0
            for d in self.predict_indiv_info
        )

        if not have_coords_pred and not have_region_ids_pred:
            raise ValueError(
                "In threshold mode, provide either (lat+lon) for all PREDICT individuals or region_ids for all."
            )
        if have_region_ids_pred and self.predict_region_info is not None:
            # if not self.predict_region_info or len(self.predict_region_info) == 0:
            #     raise ValueError("predict_region_info is required when predict_indiv_info uses region_ids.")
            max_idx = len(self.predict_region_info) - 1
            bad = []
            for i, d in enumerate(self.predict_indiv_info):
                for r in d.region_ids or []:
                    if r < 0 or r > max_idx:
                        bad.append((i, r))
            if bad:
                sample = ", ".join(
                    f"(predict indiv {i}, region {r})" for i, r in bad[:10]
                )
                raise ValueError(f"predict region_ids out of range: {sample}")

        # (optional) apply same spatial rule to FIT set if you need it too:
        have_coords_fit = all(
            d.lat is not None and d.lon is not None for d in self.fit_indiv_info
        )
        have_region_ids_fit = all(
            d.region_ids is not None and len(d.region_ids) > 0
            for d in self.fit_indiv_info
        )
        if not have_coords_fit and not have_region_ids_fit:
            raise ValueError(
                "In threshold mode, provide either (lat+lon) for all FIT individuals or region_ids for all."
            )

        return self


class StatEntry(BaseModel):
    idx: int
    stat: float
    is_signif: bool = False


class AuditResponse(BaseModel):
    sbi_score: float
    signif_thresh: float
    total_signif_regions: int
    fair_map_html: str
    fair_map_image: str
    stats: List[StatEntry]
    distribution_map_html: str
    distribution_map_image: str


class Metric(BaseModel):
    name: str
    value: float


class MitigatedPredEntry(BaseModel):
    idx: int
    y_pred: int


class RelabelingResponse(BaseModel):
    metrics_before: List[Metric]
    metrics_after: List[Metric]
    audit_before_mitigation: AuditResponse
    audit_after_mitigation: AuditResponse
    mitigated_preds: List[MitigatedPredEntry]
    flips_map_html: str
    flips_map_image: str


class ThresholdEntry(BaseModel):
    idx: int
    threshold: float
    eq_to_thresh_flip_prob: float


class ThresholdAdjustmentResponse(BaseModel):
    metrics_before: List[Metric]
    metrics_after: List[Metric]
    audit_before_mitigation: AuditResponse
    audit_after_mitigation: AuditResponse
    mitigated_preds: List[MitigatedPredEntry]
    threshold_chart_before: str
    threshold_chart_after: str
    new_thresholds: List[ThresholdEntry]
    flips_map_html: str
    flips_map_image: str
