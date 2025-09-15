# src/api/logic.py

from .models import (
    AuditRequest,
    RelabelingRequest,
    RelabelingResponse,
    Metric,
    MitigatedPredEntry,
)
import numpy as np
from app.services.spatial_bias.utils.api_visual_utils import (
    generate_distribution_map,
    generate_synthetic_flips_distribution_plot,
)
from app.services.spatial_bias.methods.models.optimization_model import (
    SpatialOptimFairnessModel,
)
from app.services.spatial_bias.utils.data_utils import get_metric, get_positive_rates
from app.services.spatial_bias.utils.geo_utils import (
    compute_map_info,
    compute_optimal_radius,
    get_regions_ch,
)
from .audit_logic import run_audit_pipeline
from app.services.spatial_bias.utils.input_utils import prepare_inputs


def run_relabel_mitigation(req: RelabelingRequest) -> RelabelingResponse:
    input_data = prepare_inputs(req)
    y_pred = input_data["y_pred"]
    y_true = input_data["y_true"]
    region_indices = input_data["region_indices"]
    lats = input_data["lats"]
    lons = input_data["lons"]
    indiv_coords_given = input_data["indiv_coords_given"]
    polygons = input_data["polygons"]
    overlap = input_data["overlap"]
    synth_layout = input_data["synth_layout"]

    # Step 2: Compute metrics before mitigation
    metrics_before = (
        [
            Metric(name="accuracy", value=get_metric("accuracy", y_true, y_pred)),
            Metric(name="precision", value=get_metric("precision", y_true, y_pred)),
            Metric(name="recall", value=get_metric("recall", y_true, y_pred)),
            Metric(name="f1", value=get_metric("f1", y_true, y_pred)),
        ]
        if y_true is not None
        else []
    )

    audit_result_before = run_audit_pipeline(
        req=AuditRequest(
            n_worlds=req.n_worlds,
            signif_level=req.signif_level,
            equal_opp=req.equal_opp,
            indiv_info=req.indiv_info,
            region_info=req.region_info,
        ),
        zoom_start=9,
        synth_layout=synth_layout,
    )

    # Step 3: Run mitigation
    model_name = "promis_app" if req.approx else "promis_opt"
    print(f"overlap: {overlap}")
    fair_model = SpatialOptimFairnessModel(model_name)
    fair_model.fit(
        points_per_region=region_indices,
        y_pred=y_pred,
        y_true=y_true if req.equal_opp else None,
        budget=req.budget_constr,
        max_pr_shift=req.pr_constr,
        wlimit=req.work_limit,
        fair_notion="statistical_parity" if not req.equal_opp else "equal_opportunity",
        overlap=overlap,
        no_of_threads=1,
        verbose=0,
    )

    # Get the new predictions
    mitigated_pred = fair_model.predict(region_indices, y_pred, apply_fit_flips=True)

    # Build new indiv_info with mitigated predictions
    mitigated_indiv_info = [
        {**ind.model_dump(), "y_pred": int(mitigated_pred[i])}
        for i, ind in enumerate(req.indiv_info)
    ]

    # Step 4: Compute metrics after mitigation
    audit_result_after = run_audit_pipeline(
        req=AuditRequest(
            n_worlds=req.n_worlds,
            signif_level=req.signif_level,
            equal_opp=req.equal_opp,
            indiv_info=mitigated_indiv_info,
            region_info=req.region_info,
        ),
        max_stat=max(
            [
                audit_result_before.stats[i].stat
                for i in range(len(audit_result_before.stats))
            ]
        ),
        zoom_start=9,
        synth_layout=synth_layout,
    )
    metrics_after = (
        [
            Metric(
                name="accuracy", value=get_metric("accuracy", y_true, mitigated_pred)
            ),
            Metric(
                name="precision", value=get_metric("precision", y_true, mitigated_pred)
            ),
            Metric(name="recall", value=get_metric("recall", y_true, mitigated_pred)),
            Metric(name="f1", value=get_metric("f1", y_true, mitigated_pred)),
        ]
        if y_true is not None
        else []
    )

    y_true = np.array(y_true) if y_true is not None else None

    if indiv_coords_given:
        flips_map_image = ""
        flips_info = [
            {
                "lat": lats[indiv_idx],
                "lon": lons[indiv_idx],
                "dir": fair_model.pts_to_change_sol[i],
            }
            for i, indiv_idx in enumerate(fair_model.pts_to_change)
        ]
        center_loc, zoom_start = compute_map_info(polygons) if polygons else (0, 0)
        _, pr_regions = get_positive_rates(
            mitigated_pred, region_indices, y_true=y_true if req.equal_opp else None
        )
        flips_map_html = generate_distribution_map(
            # indiv_info=indiv_info,
            polygons=polygons,
            flips_info=flips_info,
            regions_pr=pr_regions,
            zoom_start=zoom_start,
            center_loc=center_loc,
            pts_radius=compute_optimal_radius(
                n_points=len(flips_info), zoom=zoom_start
            ),
            tp=req.equal_opp,
        )
    else:
        flips_map_html = ""
        flips_per_region = {}
        for indiv_idx in fair_model.pts_to_change:
            region_ids = req.indiv_info[indiv_idx].region_ids
            for region_id in region_ids:
                if region_id not in flips_per_region:
                    flips_per_region[region_id] = []
                flips_per_region[region_id].append(indiv_idx)

        flips_map_image = generate_synthetic_flips_distribution_plot(
            layout=synth_layout,
            pts_per_region=flips_per_region,
            xaxis_limits=synth_layout["xlim"],
            yaxis_limits=synth_layout["ylim"],
        )

    return RelabelingResponse(
        metrics_before=metrics_before,
        metrics_after=metrics_after,
        audit_before_mitigation=audit_result_before,
        audit_after_mitigation=audit_result_after,
        mitigated_preds=[
            MitigatedPredEntry(idx=i, y_pred=int(mitigated_pred[i]))
            for i in range(len(mitigated_pred))
        ],
        flips_map_html=flips_map_html,
        flips_map_image=flips_map_image,
    )
