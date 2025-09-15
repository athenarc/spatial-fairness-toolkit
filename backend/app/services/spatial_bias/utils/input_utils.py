from app.services.spatial_bias.utils.geo_utils import (
    get_regions_ch,
    spatial_cluster_fast,
    # spatial_cluster_auto_k,
    assign_region_ids_with_strtree,
)
import numpy as np
import pandas as pd
from app.services.spatial_bias.utils.data_utils import get_regions
from app.services.spatial_bias.utils.geo_utils import generate_points_in_polygon


import math
import random
from typing import Dict, List, Sequence, Tuple
import numpy as np


def _circle_distance_ok(
    x: float,
    y: float,
    centers: List[Tuple[float, float]],
    radii: List[float],
    r_new: float,
    margin: float,
) -> bool:
    """Check if a new circle at (x, y, r_new) does not overlap any existing circle
    with an extra margin."""
    for (cx, cy), r in zip(centers, radii):
        dx = x - cx
        dy = y - cy
        if dx * dx + dy * dy < (r + r_new + margin) ** 2:
            return False
    return True


def _place_centers_non_overlapping(
    radii: Sequence[float],
    margin: float = 0.05,
    spiral_step: float = None,
    max_tries_per_circle: int = 5000,
    seed: int = 42,
) -> List[Tuple[float, float]]:
    """
    Place circle centers in 2D so that circles (given by radii) don't overlap.
    Uses a golden-angle spiral with rejection. Larger circles are placed first.
    """
    rng = random.Random(seed)
    # Work on indices sorted by descending radius
    order = sorted(range(len(radii)), key=lambda i: radii[i], reverse=True)
    centers_out = [None] * len(radii)  # type: ignore

    placed_centers: List[Tuple[float, float]] = []
    placed_radii: List[float] = []

    phi = (math.sqrt(5) - 1) / 2  # ~0.618...
    golden_angle = 2 * math.pi * (1 - phi)  # ~137.5 degrees

    # A reasonable spiral step based on max radius (spread things out)
    max_r = max(radii)
    if spiral_step is None:
        spiral_step = 2.5 * (max_r + margin)

    for idx in order:
        r_new = radii[idx]

        # Try (in order) the origin, then a sequence of spiral points
        # Slight random jitter on start angle per circle to avoid lattice effects
        base_theta = rng.random() * 2 * math.pi

        placed = False
        for k in range(max_tries_per_circle):
            if k == 0:
                # First attempt at origin
                x, y = 0.0, 0.0
            else:
                # Golden-angle spiral: radius grows like sqrt(k) for even spread
                rho = spiral_step * math.sqrt(k)
                theta = base_theta + k * golden_angle
                x = rho * math.cos(theta)
                y = rho * math.sin(theta)

            if _circle_distance_ok(x, y, placed_centers, placed_radii, r_new, margin):
                placed_centers.append((x, y))
                placed_radii.append(r_new)
                centers_out[idx] = (x, y)
                placed = True
                break

        if not placed:
            # Fallback: brute-force random placement in a large box
            # (very rare with reasonable parameters)
            for _ in range(max_tries_per_circle):
                x = rng.uniform(-100 * spiral_step, 100 * spiral_step)
                y = rng.uniform(-100 * spiral_step, 100 * spiral_step)
                if _circle_distance_ok(
                    x, y, placed_centers, placed_radii, r_new, margin
                ):
                    placed_centers.append((x, y))
                    placed_radii.append(r_new)
                    centers_out[idx] = (x, y)
                    placed = True
                    break
            if not placed:
                raise RuntimeError("Failed to place non-overlapping circles.")

    # type: ignore: centers_out fully filled
    return centers_out  # type: ignore


def _region_markersize(
    radius: float,
    n_points: int,
    ms_base: float = 3.0,
    ms_scale: float = 18.0,
    ms_min: float = 2.0,
    ms_max: float = 20.0,
) -> float:
    """
    Adaptive marker size in *points* (for Line2D markers, i.e., ax.plot).
    Scales like radius / sqrt(n_points), then affine-transformed and clamped.
    """
    if n_points <= 0:
        return ms_min
    size = ms_base + ms_scale * (radius / (n_points**0.5))
    return float(np.clip(size, ms_min, ms_max))


def precompute_synthetic_layout(
    pts_per_region: Sequence[Sequence[int]],
    y_preds: np.ndarray,
    *,
    base_radius: float = 0.25,
    radius_scale: float = 0.06,
    margin: float = 0.05,
    seed: int = 123,
):
    """
    Build a synthetic, non-overlapping layout for regions and individuals.

    Args
    ----
    pts_per_region: list-like of lists; each inner list contains the indiv indices in that region
    y_preds: array of predicted scores per individual index (same indexing as the inner lists)
    base_radius: minimum visual radius for a region (area floor)
    radius_scale: scales how much population increases area (radius grows with sqrt(n))
    margin: extra gap between circles to ensure visual separation
    seed: RNG seed for reproducibility

    Returns
    -------
    layout dict with:
      - regions[region_id] = {"center": (x, y), "radius": r}
      - individuals[indiv_id] = {"x": x, "y": y, "y_pred": y_preds[indiv_id]}
      - xlim, ylim for plotting
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    n_regions = len(pts_per_region)

    # --- Radius design: area ∝ population => radius ∝ sqrt(population) ---
    # Ensure radius stays visually reasonable even for tiny regions.
    pops = np.array([len(members) for members in pts_per_region], dtype=float)
    radii = base_radius + radius_scale * np.sqrt(np.maximum(pops, 0.0))
    print(f"radii: {radii}")

    # --- Place centers with non-overlap ---
    centers = _place_centers_non_overlapping(radii, margin=margin, seed=seed)

    layout = {
        "regions": {},
        "individuals": {},
        "xlim": None,
        "ylim": None,
    }

    all_x_edges, all_y_edges = [], []

    # Build regions & individual coordinates
    all_region_ms = []
    for region_id, members in enumerate(pts_per_region):
        cx, cy = centers[region_id]
        R = radii[region_id]
        region_ms = _region_markersize(R, len(members))
        all_region_ms.append(region_ms)
        layout["regions"][region_id] = {
            "center": (cx, cy),
            "radius": float(R),
            "ms": region_ms,
        }

        # Track plot bounds
        all_x_edges.extend([cx - R, cx + R])
        all_y_edges.extend([cy - R, cy + R])

        # Sample points uniformly inside the circle: r = R*sqrt(u), theta ~ U[0, 2π)
        # (This yields uniform AREA density)
        m = len(members)
        if m > 0:
            u = np_rng.random(m)
            r = R * np.sqrt(u)
            theta = np_rng.random(m) * 2 * math.pi
            px = cx + r * np.cos(theta)
            py = cy + r * np.sin(theta)

            for indiv, x_i, y_i in zip(members, px, py):
                # Only set once if indiv appears in multiple regions (shouldn't happen in non-overlap case)
                if indiv not in layout["individuals"]:
                    layout["individuals"][indiv] = {
                        "x": float(x_i),
                        "y": float(y_i),
                        "y_pred": float(y_preds[indiv]),
                    }
    layout["global_ms"] = np.median(all_region_ms)
    # Plot limits with padding relative to the largest radius
    padding = 0.2 + float(np.max(radii)) * 0.2 if n_regions > 0 else 0.2
    x_min, x_max = (
        (min(all_x_edges) - padding, max(all_x_edges) + padding)
        if all_x_edges
        else (-1, 1)
    )
    y_min, y_max = (
        (min(all_y_edges) - padding, max(all_y_edges) + padding)
        if all_y_edges
        else (-1, 1)
    )
    layout["xlim"] = (float(x_min), float(x_max))
    layout["ylim"] = (float(y_min), float(y_max))

    return layout


def prepare_inputs(req, synth_layout=None):
    # Step 1: Prepare inputs
    df_indiv = pd.DataFrame([indiv.model_dump() for indiv in req.indiv_info])

    y_pred = df_indiv["y_pred"].values
    y_true = df_indiv["y_true"].values if req.equal_opp else None

    indiv_coords_given = all(
        (ind.lat is not None and ind.lon is not None) for ind in req.indiv_info
    )
    region_ids_given = all(
        (ind.region_ids is not None and len(ind.region_ids) > 0)
        for ind in req.indiv_info
    )

    lats = df_indiv["lat"].values if indiv_coords_given else None
    lons = df_indiv["lon"].values if indiv_coords_given else None

    polygons = (
        [region.polygon for region in req.region_info] if req.region_info else None
    )

    if region_ids_given:
        regions_ids = df_indiv["region_ids"].values
    elif indiv_coords_given and polygons is not None:
        regions_ids = assign_region_ids_with_strtree(
            [[lat, lon] for lat, lon in zip(lats, lons)], polygons
        )
    elif indiv_coords_given:
        regions_ids = spatial_cluster_fast(np.column_stack((lats, lons)))
    else:
        raise ValueError(
            "Neither region IDs nor coordinates provided; cannot partition space."
        )

    region_indices = get_regions(regions_ids)

    polygons = (
        get_regions_ch(region_indices, lats, lons)
        if polygons is None and indiv_coords_given
        else polygons
    )

    if polygons is not None and not indiv_coords_given:
        poly_pts = [
            generate_points_in_polygon(polygons[i], len(region_indices[i]))
            for i in range(len(polygons))
        ]
        all_poly_pts = [pt for sublist in poly_pts for pt in sublist]
        lats = [pt[0] for pt in all_poly_pts]
        lons = [pt[1] for pt in all_poly_pts]
        indiv_coords_given = True

    overlap = any(len(reg_id) > 1 for reg_id in regions_ids)

    synth_layout = (
        precompute_synthetic_layout(region_indices, y_preds=y_pred)
        if synth_layout is None and not indiv_coords_given and polygons is None
        else synth_layout
    )

    input_data = {
        "y_pred": y_pred,
        "y_true": y_true,
        "region_indices": region_indices,
        "lats": lats,
        "lons": lons,
        "indiv_coords_given": indiv_coords_given,
        "polygons": polygons,
        "overlap": overlap,
        "synth_layout": synth_layout,
    }

    return input_data


def prepare_inputs_thresholds(req):
    req_filled = req.model_copy(deep=True)

    # Step 1: Prepare inputs
    df_indiv_train = pd.DataFrame([indiv.model_dump() for indiv in req.fit_indiv_info])
    df_indiv_test = pd.DataFrame(
        [indiv.model_dump() for indiv in req.predict_indiv_info]
    )

    y_pred_train = df_indiv_train["y_pred"].values
    y_true_train = df_indiv_train["y_true"].values if req.equal_opp else None
    y_pred_probs_train = df_indiv_train["y_pred_prob"].values

    y_pred_test = df_indiv_test["y_pred"].values
    # y_true_test = (
    #     df_indiv_test["y_true"].values
    #     if df_indiv_test["y_true"].notnull().any()
    #     else None
    # )
    y_true_test = (
        None
        if df_indiv_test["y_true"].isnull().any()
        else df_indiv_test["y_true"].values
    )
    y_pred_probs_test = df_indiv_test["y_pred_prob"].values

    indiv_coords_train_given = (
        df_indiv_train["lat"].notnull().all() and df_indiv_train["lon"].notnull().all()
    )

    indiv_coords_test_given = (
        df_indiv_test["lat"].notnull().all() and df_indiv_test["lon"].notnull().all()
    )

    indiv_coords_given = indiv_coords_train_given and indiv_coords_test_given

    region_ids_given = (
        df_indiv_train["region_ids"].notnull().all()
        and df_indiv_test["region_ids"].notnull().all()
    )

    lats_train = df_indiv_train["lat"].values if indiv_coords_train_given else None
    lons_train = df_indiv_train["lon"].values if indiv_coords_train_given else None
    lats_test = df_indiv_test["lat"].values if indiv_coords_test_given else None
    lons_test = df_indiv_test["lon"].values if indiv_coords_test_given else None

    polygons = (
        [region.polygon for region in req.predict_region_info]
        if req.predict_region_info
        else None
    )

    if region_ids_given:
        regions_ids_train = df_indiv_train["region_ids"].values
        regions_ids_test = df_indiv_test["region_ids"].values
    elif indiv_coords_given and polygons is not None:
        regions_ids_train = assign_region_ids_with_strtree(
            [[lat, lon] for lat, lon in zip(lats_train, lons_train)], polygons
        )
        regions_ids_test = assign_region_ids_with_strtree(
            [[lat, lon] for lat, lon in zip(lats_test, lons_test)], polygons
        )

        req_filled.fit_indiv_info = [
            ind.copy(update={"region_ids": reg_id})
            for ind, reg_id in zip(req_filled.fit_indiv_info, regions_ids_train)
        ]
        req_filled.predict_indiv_info = [
            ind.copy(update={"region_ids": reg_id})
            for ind, reg_id in zip(req_filled.predict_indiv_info, regions_ids_test)
        ]
    elif indiv_coords_given:
        all_lats = np.concatenate((lats_train, lats_test))
        all_lons = np.concatenate((lons_train, lons_test))
        regions_ids = spatial_cluster_fast(np.column_stack((all_lats, all_lons)))
        regions_ids_train = regions_ids[: len(lats_train)]
        regions_ids_test = regions_ids[len(lats_train) :]
        req_filled.fit_indiv_info = [
            ind.copy(update={"region_ids": reg_id})
            for ind, reg_id in zip(req_filled.fit_indiv_info, regions_ids_train)
        ]
        req_filled.predict_indiv_info = [
            ind.copy(update={"region_ids": reg_id})
            for ind, reg_id in zip(req_filled.predict_indiv_info, regions_ids_test)
        ]
    else:
        raise ValueError(
            "Neither region IDs nor coordinates provided; cannot partition space."
        )

    region_indices_train = get_regions(regions_ids_train)
    region_indices_test = get_regions(regions_ids_test)

    polygons = (
        get_regions_ch(region_indices_test, lats_test, lons_test)
        if polygons is None and indiv_coords_test_given
        else polygons
    )

    if polygons and not req_filled.predict_region_info:
        req_filled.predict_region_info = [{"polygon": poly} for poly in polygons]

    if polygons is not None and not indiv_coords_test_given:
        poly_pts = [
            generate_points_in_polygon(polygons[i], len(region_indices_test[i]))
            for i in range(len(polygons))
        ]
        all_poly_pts = [pt for sublist in poly_pts for pt in sublist]
        lats_test = [pt[0] for pt in all_poly_pts]
        lons_test = [pt[1] for pt in all_poly_pts]
        indiv_coords_test_given = True
        req_filled.predict_indiv_info = [
            ind.copy(update={"lat": lat, "lon": lon})
            for ind, lat, lon in zip(
                req_filled.predict_indiv_info, lats_test, lons_test
            )
        ]

    overlap = any(len(reg_id) > 1 for reg_id in regions_ids_train) or any(
        len(reg_id) > 1 for reg_id in regions_ids_test
    )

    synth_layout = (
        precompute_synthetic_layout(
            pts_per_region=region_indices_test, y_preds=y_pred_test
        )
        if not indiv_coords_given and polygons is None
        else None
    )

    input_data = {
        "y_pred_train": y_pred_train,
        "y_true_train": y_true_train,
        "y_pred_probs_train": y_pred_probs_train,
        "region_indices_train": region_indices_train,
        "lats_train": lats_train,
        "lons_train": lons_train,
        "indiv_coords_train_given": indiv_coords_train_given,
        "y_pred_test": y_pred_test,
        "y_true_test": y_true_test,
        "y_pred_probs_test": y_pred_probs_test,
        "region_indices_test": region_indices_test,
        "lats_test": lats_test,
        "lons_test": lons_test,
        "indiv_coords_test_given": indiv_coords_test_given,
        "polygons": polygons,
        "overlap": overlap,
        "synth_layout": synth_layout,
    }

    return input_data, req_filled
