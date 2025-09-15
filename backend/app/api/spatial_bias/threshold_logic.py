# src/api/logic.py

from .models import (
    AuditRequest,
    ThresholdAdjustmentRequest,
    ThresholdAdjustmentResponse,
    Metric,
    ThresholdEntry,
    MitigatedPredEntry,
)
import numpy as np
from app.services.spatial_bias.utils.api_visual_utils import (
    generate_threshold_chart_base64,
    generate_distribution_map,
    generate_synthetic_flips_distribution_plot,
)
from app.services.spatial_bias.methods.models.optimization_model import (
    SpatialOptimFairnessModel,
)
from app.services.spatial_bias.utils.data_utils import (
    get_metric,
    get_positive_rates,
)
from app.services.spatial_bias.utils.scores import get_fair_stat_ratios
from app.services.spatial_bias.utils.geo_utils import (
    compute_map_info,
    compute_optimal_radius,
)
from .audit_logic import run_audit_pipeline
from app.services.spatial_bias.utils.input_utils import prepare_inputs_thresholds


def run_threshold_mitigation(
    req: ThresholdAdjustmentRequest,
) -> ThresholdAdjustmentResponse:

    # Step 1: Prepare inputs
    input_data, req = prepare_inputs_thresholds(req)

    y_pred_train = input_data["y_pred_train"]
    y_true_train = input_data["y_true_train"]
    y_pred_probs_train = input_data["y_pred_probs_train"]
    region_indices_train = input_data["region_indices_train"]
    # lats_train = input_data["lats_train"]
    # lons_train = input_data["lons_train"]
    # indiv_coords_train_given = input_data["indiv_coords_train_given"]

    y_pred_test = input_data["y_pred_test"]
    y_true_test = input_data["y_true_test"]
    y_pred_probs_test = input_data["y_pred_probs_test"]
    region_indices_test = input_data["region_indices_test"]
    lats_test = input_data["lats_test"]
    lons_test = input_data["lons_test"]
    indiv_coords_test_given = input_data["indiv_coords_test_given"]

    polygons = input_data["polygons"]
    overlap = input_data["overlap"]

    synth_layout = input_data["synth_layout"]

    # Step 2: Compute metrics before mitigation
    metrics_before = (
        [
            Metric(
                name="accuracy", value=get_metric("accuracy", y_true_test, y_pred_test)
            ),
            Metric(
                name="precision",
                value=get_metric("precision", y_true_test, y_pred_test),
            ),
            Metric(name="recall", value=get_metric("recall", y_true_test, y_pred_test)),
            Metric(name="f1", value=get_metric("f1", y_true_test, y_pred_test)),
        ]
        if y_true_test is not None
        else []
    )

    audit_result_before = run_audit_pipeline(
        req=AuditRequest(
            n_worlds=req.n_worlds,
            signif_level=req.signif_level,
            equal_opp=req.equal_opp,
            indiv_info=req.predict_indiv_info,
            region_info=req.predict_region_info,
        ),
        zoom_start=9,
        synth_layout=synth_layout,
    )

    max_stat = max(
        [
            audit_result_before.stats[i].stat
            for i in range(len(audit_result_before.stats))
        ]
    )

    print(f"overlap: {overlap}")

    # Step 3: Run mitigation
    model_name = "promis_app" if req.approx else "promis_opt"

    fair_model = SpatialOptimFairnessModel(model_name)
    fair_model.fit(
        points_per_region=region_indices_train,
        y_pred=y_pred_train,
        y_pred_probs=y_pred_probs_train,
        y_true=y_true_train if req.equal_opp else None,
        init_threshold=req.default_boundary,
        budget=req.budget_constr,
        max_pr_shift=req.pr_constr,
        wlimit=req.work_limit,
        fair_notion="statistical_parity" if not req.equal_opp else "equal_opportunity",
        overlap=overlap,
        no_of_threads=1,
        verbose=0,
    )

    # Get the new predictions
    mitigated_pred = fair_model.predict(
        region_indices_test, y_pred_probs_test, apply_fit_flips=False
    )

    mitigated_indiv_info = []
    for i, ind in enumerate(req.predict_indiv_info):
        new_ind = ind.model_dump()
        new_ind["y_pred"] = int(mitigated_pred[i])
        new_ind.pop("y_pred_prob", None)  # remove to comply with AuditRequest
        mitigated_indiv_info.append(new_ind)

    # Step 4: Compute metrics after mitigation
    audit_result_after = run_audit_pipeline(
        req=AuditRequest(
            n_worlds=req.n_worlds,
            signif_level=req.signif_level,
            equal_opp=req.equal_opp,
            indiv_info=mitigated_indiv_info,
            region_info=req.predict_region_info,
        ),
        max_stat=max_stat,
        zoom_start=9,
        synth_layout=synth_layout,
    )
    metrics_after = (
        [
            Metric(
                name="accuracy",
                value=get_metric("accuracy", y_true_test, mitigated_pred),
            ),
            Metric(
                name="precision",
                value=get_metric("precision", y_true_test, mitigated_pred),
            ),
            Metric(
                name="recall", value=get_metric("recall", y_true_test, mitigated_pred)
            ),
            Metric(name="f1", value=get_metric("f1", y_true_test, mitigated_pred)),
        ]
        if y_true_test is not None
        else []
    )

    # Step 5: Compute fairness normalized statistics

    stats_before = [
        audit_result_before.stats[i].stat for i in range(len(audit_result_before.stats))
    ]
    stats_after = [
        audit_result_after.stats[i].stat for i in range(len(audit_result_after.stats))
    ]

    PR_test_before, pr_regions_before = get_positive_rates(
        y_pred_test, region_indices_test, y_true=y_true_test if req.equal_opp else None
    )
    PR_test_after, pr_regions_after = get_positive_rates(
        mitigated_pred,
        region_indices_test,
        y_true=y_true_test if req.equal_opp else None,
    )

    regions_fair_stats_before, _ = get_fair_stat_ratios(
        stats=stats_before,
        pr_s=pr_regions_before,
        PR=PR_test_before,
        cap=max_stat,
        t=audit_result_before.signif_thresh,
    )

    regions_fair_stats_after, _ = get_fair_stat_ratios(
        stats=stats_after,
        pr_s=pr_regions_after,
        PR=PR_test_after,
        cap=max_stat,
        t=audit_result_after.signif_thresh,
    )

    y_pred_diff = np.array(mitigated_pred) - np.array(y_pred_test)
    y_true_test = np.array(y_true_test) if y_true_test is not None else None
    indices_of_interest = (
        np.where((y_pred_diff != 0) & (y_true_test == 1))[0]
        if req.equal_opp
        else np.where(y_pred_diff != 0)[0]
    )

    if indiv_coords_test_given:
        flips_map_image = ""

        flips_info = [
            {
                "lat": lats_test[indiv_idx],
                "lon": lons_test[indiv_idx],
                "dir": 1 if y_pred_diff[indiv_idx] > 0 else -1,
            }
            for indiv_idx in indices_of_interest
        ]

        center_loc, zoom_start = compute_map_info(polygons) if polygons else (0, 0)
        _, pr_regions = get_positive_rates(
            mitigated_pred,
            region_indices_test,
            y_true=y_true_test if req.equal_opp else None,
        )
        flips_map = generate_distribution_map(
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
        flips_map = ""
        flips_per_region = {}
        for indiv_idx in indices_of_interest:
            region_ids = req.predict_indiv_info[indiv_idx].region_ids
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

    return ThresholdAdjustmentResponse(
        metrics_before=metrics_before,
        metrics_after=metrics_after,
        audit_before_mitigation=audit_result_before,
        audit_after_mitigation=audit_result_after,
        mitigated_preds=[
            MitigatedPredEntry(idx=i, y_pred=int(mitigated_pred[i]))
            for i in range(len(mitigated_pred))
        ],
        threshold_chart_before=generate_threshold_chart_base64(
            [req.default_boundary] * len(region_indices_test),
            regions_fair_stats_before,
            title="",
        ),
        threshold_chart_after=generate_threshold_chart_base64(
            fair_model.thresholds, regions_fair_stats_after, title=""
        ),
        new_thresholds=[
            ThresholdEntry(
                idx=i,
                threshold=fair_model.thresholds[i],
                eq_to_thresh_flip_prob=fair_model.eq_to_thresh_flip_probs[i],
            )
            for i in range(len(fair_model.thresholds))
        ],
        flips_map_html=flips_map,
        flips_map_image=flips_map_image,
    )
