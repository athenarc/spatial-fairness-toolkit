# src/api/logic.py

from .models import (
    AuditRequest,
    AuditResponse,
    StatEntry,
)
import numpy as np
import pandas as pd
from app.services.spatial_bias.methods.audit import run_spatial_audit
from app.services.spatial_bias.utils.api_visual_utils import (
    generate_fairness_map_html,
    generate_distribution_map,
    generate_synthetic_distribution_plot,
    generate_synthetic_fairness_map_plot,
)
from app.services.spatial_bias.utils.data_utils import get_positive_rates
from app.services.spatial_bias.utils.scores import (
    get_fair_stat_ratios,
)
from app.services.spatial_bias.utils.geo_utils import (
    compute_map_info,
    compute_optimal_radius,
)
from app.services.spatial_bias.utils.input_utils import prepare_inputs


def run_audit_pipeline(
    req: AuditRequest, max_stat=None, zoom_start=9, synth_layout=None
) -> AuditResponse:

    input_data = prepare_inputs(req=req, synth_layout=synth_layout)
    y_pred = input_data["y_pred"]
    y_true = input_data["y_true"]
    region_indices = input_data["region_indices"]
    lats = input_data["lats"]
    lons = input_data["lons"]
    indiv_coords_given = input_data["indiv_coords_given"]
    polygons = input_data["polygons"]
    synth_layout = input_data["synth_layout"]

    # Step 2: Run audit
    df_scanned, signif_thresh, sbi_score = run_spatial_audit(
        y_pred=y_pred,
        y_true=y_true if req.equal_opp else None,
        region_indices=region_indices,
        signif_level=req.signif_level,
        n_worlds=req.n_worlds,
    )

    # Step 3: Generate visual outputs
    stats = df_scanned["statistic"].tolist()
    max_stat = max(stats) if max_stat is None else max_stat

    PR, pr_regions = get_positive_rates(
        y_pred, region_indices, y_true=y_true if req.equal_opp else None
    )

    regions_fair_stats, _ = get_fair_stat_ratios(
        stats=stats,
        pr_s=pr_regions,
        PR=PR,
        t=signif_thresh,
        cap=max_stat,
    )

    center_loc, zoom_start = compute_map_info(polygons) if polygons else (0, 0)

    map_html = (
        generate_fairness_map_html(
            polygons=polygons,
            init_scores=stats,
            norm_scores=regions_fair_stats,
            signif_indices=df_scanned[df_scanned["signif"]].index.tolist(),
            zoom_start=zoom_start,
            center_loc=center_loc,
        )
        if polygons
        else ""
    )

    map_image = (
        generate_synthetic_fairness_map_plot(
            scores=regions_fair_stats,
            signif_indices=df_scanned[df_scanned["signif"]].index.tolist(),
            regions_layout=synth_layout["regions"],
            xaxis_limits=synth_layout["xlim"],
            yaxis_limits=synth_layout["ylim"],
        )
        if not map_html
        else ""
    )

    y_true = np.array(y_true) if y_true is not None else None
    indiv_indices = (
        np.where(y_true == 1)[0] if req.equal_opp else np.arange(len(y_pred))
    )
    if indiv_coords_given:
        distribution_map_image = ""
        indiv_info = [
            {"lat": lats[i], "lon": lons[i], "pred": y_pred[i]} for i in indiv_indices
        ]
        pts_radius = compute_optimal_radius(n_points=len(indiv_info), zoom=zoom_start)

        distribution_map_html = generate_distribution_map(
            indiv_info=indiv_info,
            polygons=polygons,
            regions_pr=pr_regions,
            zoom_start=zoom_start,
            center_loc=center_loc,
            pts_radius=pts_radius,
            tp=req.equal_opp,
        )
    else:
        distribution_map_html = ""
        distribution_map_image = generate_synthetic_distribution_plot(
            layout=synth_layout,
            pts_per_region=region_indices,
            xaxis_limits=synth_layout["xlim"],
            yaxis_limits=synth_layout["ylim"],
            tp=req.equal_opp,
        )

    return AuditResponse(
        sbi_score=sbi_score,
        signif_thresh=signif_thresh,
        total_signif_regions=int(df_scanned["signif"].sum()),
        fair_map_html=map_html,
        fair_map_image=map_image,
        stats=[
            StatEntry(idx=i, stat=stat, is_signif=bool(df_scanned["signif"][i]))
            for i, stat in enumerate(stats)
        ],
        distribution_map_html=distribution_map_html,
        distribution_map_image=distribution_map_image,
    )
