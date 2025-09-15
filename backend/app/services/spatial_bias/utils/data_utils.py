import pandas as pd
import numpy as np
from ast import literal_eval
from app.services.spatial_bias.methods.models.optimization_model import (
    SpatialOptimFairnessModel,
)
import os


#### The dataframe should have columns lat, lon, label
def load_data(filename):
    """
    Loads data from a CSV file and resets the index.

    Args:
        filename (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with the loaded data, index reset.
    """
    df = pd.read_csv(filename, index_col=0)
    df.reset_index(drop=True, inplace=True)

    return df


def get_y(df, label):
    """
    Extracts the specified label column from the DataFrame as a list

    Args:
        df (pd.DataFrame): DataFrame containing the label column.
        label (str): Column name for the labels.

    Returns:
        np.ndarray: List with the values of the specified column
    """

    array = np.array(df[label].values.tolist())

    return array


def read_scanned_regs(input_path):
    """
    Reads a CSV file containing scanned regions and parses the 'points' column as Python objects.

    Args:
        input_path (str): Path to the CSV file with scanned regions.

    Returns:
        pd.DataFrame: DataFrame with the scanned regions and parsed 'points' column.
    """

    df_scanned_regs = pd.read_csv(input_path)
    df_scanned_regs["points"] = df_scanned_regs["points"].apply(literal_eval)
    if "new_regions_ids" in df_scanned_regs.columns:
        df_scanned_regs["new_regions_ids"] = df_scanned_regs["new_regions_ids"].apply(
            literal_eval
        )

    return df_scanned_regs


def read_all_models(folder_path, optim_methods, methods=[]):
    """
    Reads and loads all pretrained fairness models from a specified folder.

    Args:
        folder_path (str): The path to the folder containing the model files.
        optim_methods (bool): If True, loads `SpatialOptimFairnessModel`,
                              otherwise loads `SpatialFlipFairnessModel`.
        methods (list, optional): A list of specific methods to load. If empty,
                                  all available methods are loaded.

    Returns:
        dict: A dictionary mapping method names to their corresponding model instances.

    Processing steps:
        - Lists all `.pkl` files in the given folder.
        - Iterates through the files and loads the respective model (`SpatialOptimFairnessModel`
          if `optim_methods` is True, else `SpatialFlipFairnessModel`).
        - If `methods` is specified, only models matching those methods are loaded.
    """

    all_files = os.listdir(folder_path)
    all_files = [f for f in all_files if f.endswith(".pkl")]
    methods_2_models = {}
    for file in all_files:
        method_name = file.replace(".pkl", "")
        if optim_methods:
            model = SpatialOptimFairnessModel.from_pretrained(f"{folder_path}{file}")
            if methods:
                if method_name in methods:
                    methods_2_models[method_name] = model
            else:
                methods_2_models[method_name] = model
    return methods_2_models


def get_pos_info_regions(y_true, points_per_region):
    """
    Extracts positive class indices and maps them to their respective regions.

    Args:
        y_true (list or np.array): A list or array of true labels.
        points_per_region (list of lists): A list where each element is a list
                                           of indices representing a region.

    Returns:
        tuple:
            - pos_y_true_indices (np.array): Indices of points where `y_true` is 1.
            - pos_points_per_region (list of lists): A list of regions with remapped indices
                                                     for the positive class.

    """

    pos_y_true_indices = np.where(np.array(y_true) == 1)[0]
    point_2_new_pos_set_idx = {point: i for i, point in enumerate(pos_y_true_indices)}

    pos_points_per_region = [[] for _ in range(len(points_per_region))]
    for region_idx, pts in enumerate(points_per_region):
        for point in pts:
            if point in pos_y_true_indices:
                pos_points_per_region[region_idx].append(point_2_new_pos_set_idx[point])

    return pos_y_true_indices, pos_points_per_region


def get_metric(metric_name, y_true, y_pred):
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    if metric_name == "accuracy":
        return accuracy_score(y_true, y_pred)
    elif metric_name == "precision":
        return precision_score(y_true, y_pred, zero_division=0)
    elif metric_name == "recall":
        return recall_score(y_true, y_pred, zero_division=0)
    elif metric_name == "f1":
        return f1_score(y_true, y_pred, zero_division=0)
    else:
        raise ValueError(f"Unknown metric: {metric_name}")


def get_positive_rates(y_pred, regions, y_true=None):
    y_pred = np.array(y_pred)
    if y_true is not None:
        y_true = np.array(y_true)
        # For equal opportunity, we need to compute the positive regions
        pos_y_true_indices, pos_points_per_region = get_pos_info_regions(
            y_true, regions
        )
        y_pred_pos = y_pred[pos_y_true_indices]

        PR = np.sum(y_pred_pos) / len(pos_y_true_indices)
        pr_regions = [
            np.sum(y_pred_pos[pos_points_per_region[i]]) / len(pos_points_per_region[i])
            for i in range(len(pos_points_per_region))
        ]

        return PR, pr_regions

    PR = np.sum(y_pred) / len(y_pred)
    pr_regions = [
        np.sum(y_pred[regions[i]]) / len(regions[i]) for i in range(len(regions))
    ]
    return PR, pr_regions


def get_regions(reg_ids_per_individual):
    all_reg_ids = [reg_id for reg_ids in reg_ids_per_individual for reg_id in reg_ids]
    unique_regions = set(all_reg_ids)
    regions = {region_id: [] for region_id in unique_regions}
    for i, region_ids in enumerate(reg_ids_per_individual):
        for region_id in region_ids:
            regions[region_id].append(i)

    sorted_regions_ids = sorted(regions.keys())
    sorted_regions = [regions[region_id] for region_id in sorted_regions_ids]
    return sorted_regions
