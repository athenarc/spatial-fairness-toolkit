# src/analysis/audit_utils.py
import numpy as np
import pandas as pd


def run_spatial_audit(y_pred, y_true, region_indices, signif_level=0.005, n_worlds=400):
    # print(f"input:")
    # print(f"y_pred: {y_pred}")
    # print(f"y_true: {y_true}")
    # print(f"region_mapping: {region_indices}")

    from app.services.spatial_bias.utils.audit_utils import (
        get_signif_thresh_scanned_regions,
    )

    df_scanned_regs, signif_thresh = get_signif_thresh_scanned_regions(
        signif_level=signif_level,
        n_alt_worlds=n_worlds,
        regions=region_indices,
        y_pred=y_pred,
        y_true=y_true,
        seed=42,
    )

    sbi = np.mean(df_scanned_regs["statistic"])
    return df_scanned_regs, signif_thresh, sbi
