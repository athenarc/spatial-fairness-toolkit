import numpy as np
import pandas as pd
from app.services.spatial_bias.utils.scores import (
    compute_statistic,
    compute_statistic_l0_l1,
)
import math
from app.services.spatial_bias.utils.data_utils import get_pos_info_regions


def get_random_types(N, P, seed=None):
    """
    Generates a random binary array representing types based on a binomial distribution.

    Args:
        N (int): Total number of elements.
        P (int): Total number of positive elements.
        seed (int, optional): Seed for reproducibility. Defaults to None.

    Returns:
        np.ndarray: A binary array of size N with approximately P positive values.
    """

    if seed is not None:
        np.random.seed(seed)
    return np.random.binomial(size=N, n=1, p=P / N)


# def scan_regions(regions, types, N, P, verbose=False):
#     """
#     Computes the statistic for each region and identifies the region with the highest likelihood.

#     Args:
#         regions (list): List of region dictionaries, each containing "points".
#         types (np.ndarray): Binary array indicating type assignment.
#         N (int): Total number of elements.
#         P (int): Total number of positive elements.
#         verbose (bool, optional): If True, prints additional information. Defaults to False.

#     Returns:
#         tuple: The best region dictionary, the maximum likelihood value, and a list of statistics for all regions.
#     """

#     statistics = []

#     for region in regions:
#         n, p, _ = get_simple_stats(region["points"], types)
#         statistics.append(compute_statistic(n, p, N, P))

#     idx = np.argmax(statistics)

#     max_likelihood = statistics[idx]

#     if verbose:
#         print("range", np.amin(statistics), np.amax(statistics))
#         print("max likelihood", max_likelihood)
#         n, p, _ = get_simple_stats(regions[idx]["points"], types)
#         compute_statistic(n, p, N, P, verbose=verbose)

#     return regions[idx], max_likelihood, statistics


# def get_signif_threshold(
#     signif_level, n_alt_worlds, regions, N, P, seed=None, verbose=False
# ):
#     """
#     Computes the significance threshold based on alternative worlds.

#     Args:
#         signif_level (float): Significance level (e.g., 0.05 for 5% significance).
#         n_alt_worlds (int): Number of alternative worlds to generate.
#         regions (list): List of regions.
#         N (int): Total number of elements.
#         P (int): Total number of positive elements.
#         seed (int, optional): Seed for reproducibility. Defaults to None.
#         verbose (bool, optional): If True, prints additional information. Defaults to False.

#     Returns:
#         float: The computed significance threshold.
#     """

#     alt_worlds, _ = scan_alt_worlds(n_alt_worlds, regions, N, P, seed, verbose)

#     k = int(signif_level * n_alt_worlds)

#     signif_thresh = alt_worlds[k][2]  ## get the max likelihood at position k

#     return signif_thresh


# def scan_alt_worlds(n_alt_worlds, regions, N, P, seed=None, verbose=False):
#     """
#     Scans multiple alternative worlds and ranks them by maximum likelihood.

#     Args:
#         n_alt_worlds (int): Number of alternative worlds to generate.
#         regions (list): List of regions.
#         N (int): Total number of elements.
#         P (int): Total number of positive elements.
#         seed (int, optional): Seed for reproducibility. Defaults to None.
#         verbose (bool, optional): If True, prints additional information. Defaults to False.

#     Returns:
#         tuple: A list of alternative worlds sorted by likelihood and the highest likelihood value.
#     """

#     alt_worlds = []
#     current_seed = seed

#     for _ in range(n_alt_worlds):
#         alt_types = get_random_types(N, P, current_seed)
#         cur_P = np.sum(alt_types)
#         alt_best_region, alt_max_likeli, _ = scan_regions(
#             regions, alt_types, N, cur_P, verbose=verbose
#         )
#         alt_worlds.append((alt_types, alt_best_region, alt_max_likeli))

#         if current_seed is not None:
#             current_seed += 1

#     alt_worlds.sort(key=lambda x: -x[2])

#     return alt_worlds, alt_worlds[0][2]


def get_stats(df, label):
    """
    Computes basic statistics for a given dataset and label.

    Args:
        df (pd.DataFrame): Dataframe containing the data.
        label (str): The column name used to count occurrences.

    Returns:
        tuple: Total number of samples (N) and the count of positive samples (P).
    """

    N = len(df)
    P = df.loc[df[label] == 1, label].count()

    return N, P


def get_simple_stats(points, types):
    """
    Computes the number of points, number of positive cases, and their ratio.

    Args:
        points (list): List of point indices.
        types (np.ndarray): Binary array indicating type assignment.

    Returns:
        tuple: Number of points (n), number of positives (p), and ratio (rho).
    """

    n = len(points)
    p = types[points].sum()
    if n > 0:
        rho = p / n
    else:
        rho = np.nan

    return (n, p, rho)


def id2loc(df, point_id):
    """
    Retrieves latitude and longitude for a given point ID.

    Args:
        df (pd.DataFrame): Dataframe containing geographical data.
        point_id (int): Index of the point.

    Returns:
        tuple: Latitude and longitude of the specified point.
    """

    lat = df.loc[[point_id]]["lat"].values[0]
    lon = df.loc[[point_id]]["lon"].values[0]

    return (lat, lon)


def get_total_signif_regs(labels, points_per_region, sign_thres):
    """
    Counts the number of significant regions based on a given threshold.

    Args:
        labels (np.ndarray): Binary labels indicating positive cases.
        points_per_region (list): List of regions, each containing point indices.
        sign_thres (float): Significance threshold.

    Returns:
        int: Number of significant regions.
    """

    P = np.sum(labels)
    N = len(labels)
    cnt = 0

    for i in range(len(points_per_region)):
        n = len(points_per_region[i])
        p = np.sum(labels[points_per_region[i]])
        stat_i = compute_statistic(n, p, N, P)
        if stat_i > sign_thres:
            cnt += 1

    return cnt


def are_all_regions_fair(points_per_region, y_pred, signif_thresh, P=None):
    """
    Checks if all regions satisfy the fairness constraint.

    Args:
        points_per_region (list): List of regions, each containing point indices.
        y_pred (np.ndarray): Predicted labels.
        signif_thresh (float): Significance threshold.
        P (int, optional): Total number of positive predictions. If None, it is computed.

    Returns:
        bool: True if all regions are fair, False otherwise.
    """

    N = len(y_pred)

    if P == None:
        P = np.sum(y_pred)

    for pts in points_per_region:
        n = len(pts)
        p = np.sum(y_pred[pts])
        stat = compute_statistic(n, p, N, P)
        if stat >= signif_thresh:
            return False

    return True


def compute_max_likeli(n, p, N, P, verbose=False):
    """
    Computes the maximum likelihood (l1max) for a given region, comparing it to the global likelihood (l0max).

    Args:
        n (int): Number of points in the region.
        p (int): Number of positive labels in the region.
        N (int): Total number of points.
        P (int): Total number of positive labels.
        verbose (bool, optional): If True, prints intermediate steps. Defaults to False.

    Returns:
        float: The maximum likelihood value for the region.
    """

    ## handle extreme cases
    rho = P / N
    if rho == 1 or rho == 0:
        l0max = 0
    else:
        l0max = P * math.log(rho) + (N - P) * math.log(1 - rho)

    if n == 0 or n == N:  ## rho_in == 0/0 or rho_out == 0/0
        l1max = l0max
        if verbose:
            print("n == 0 or n == N")
        return l1max

    rho_in = p / n
    rho_out = (P - p) / (N - n)

    ##########################################################################
    if rho_in == rho_out:
        if verbose:
            print("p/n == (P-p)/(N-n)")
        return l0max
    ##########################################################################
    # both bin are 0
    elif (p == n or p == 0) and (p == P or N - n == P - p):
        if verbose:
            print("p == n and p == P")

        l1max = 0
    elif p == 0:  ## rho_in == 0
        if verbose:
            print("rho_in == 0")

        l1max = P * math.log(rho_out) + (N - n - P) * math.log(1 - rho_out)
    elif p == n:  ## rho_in == 1
        if verbose:
            print("p == n")

        l1max = (P - p) * math.log(rho_out) + (N - P) * math.log(1 - rho_out)
    elif p == P:  ## rho_out == 0
        if verbose:
            print("p == P")

        l1max = p * math.log(rho_in) + (n - p) * math.log(1 - rho_in)
    elif (P - p) / (N - n) == 1:  # rho_out == 1
        if verbose:
            print("P-p == N-n")

        l1max = p * math.log(rho_in) + (n - p) * math.log(1 - rho_in)
    else:
        if verbose:
            print(
                f"{rho_in=}, {rho_out=}, 1-rho_in: {1-rho_in}, 1-rho_out: {1-rho_out}"
            )

        l1max = (
            p * math.log(rho_in)
            + (n - p) * math.log(1 - rho_in)
            + (P - p) * math.log(rho_out)
            + (N - n - (P - p)) * math.log(1 - rho_out)
        )

    return l1max


def compute_statistic(n, p, N, P, verbose=False):
    """
    Computes the test statistic (l1max - l0max) for evaluating fairness in a region.

    Args:
        n (int): Number of points in the region.
        p (int): Number of positive labels in the region.
        N (int): Total number of points.
        P (int): Total number of positive labels.
        verbose (bool, optional): If True, prints intermediate steps. Defaults to False.

    Returns:
        float: The test statistic value.
    """

    ## l1max - l0max

    if verbose:
        print(f"{n=}, {p=}, {N=}, {P=}")

    if n == 0 or n == N:  ## rho_in == 0/0 or rho_out == 0/0
        if verbose:
            print("n == 0 or n == N")
        return 0

    rho = P / N
    rho_in = p / n
    rho_out = (P - p) / (N - n)

    if verbose:
        print(f"{rho=}, {rho_in=}, {rho_out=}")

    if rho == 1 or rho == 0:
        if verbose:
            print("rho == 1 or rho == 0 -> l0max = 0")
        l0max = 0
    else:
        l0max = P * math.log(rho) + (N - P) * math.log(1 - rho)

    if verbose:
        print(f"{l0max=}")

    l1max = compute_max_likeli(n, p, N, P, verbose)
    if verbose:
        print(f"{l1max=}")

    statistic = l1max - l0max

    # l1max = p*math.log(rho_in) + (n-p)*math.log(1-rho_in) + (P-p)*math.log(rho_out) + (N-n - (P-p))*math.log(1-rho_out)
    # l0max = P*math.log(rho) + (N-P)*math.log(1-rho)

    if verbose:
        print(f"{l0max=}, {l1max=}, {statistic=}")

    return statistic


def scan_regions(regions, types, N, P, verbose=False):
    """
    Computes the statistic for each region and identifies the region with the highest likelihood.

    Args:
        regions (list): List of region dictionaries, each containing "points".
        types (np.ndarray): Binary array indicating type assignment.
        N (int): Total number of elements.
        P (int): Total number of positive elements.
        verbose (bool, optional): If True, prints additional information. Defaults to False.

    Returns:
        tuple: The best region dictionary, the maximum likelihood value, and a list of statistics for all regions.
    """

    # print(f"regions: {regions}")
    # print(f"types: {types}")

    statistics = []
    max_likelihood = -np.inf
    for region in regions:
        n, p, _ = get_simple_stats(region, types)
        _, l0, l1_i = compute_statistic_l0_l1(n, p, N, P)
        cur_stat = 1 - l1_i / l0
        # cur_stat = compute_statistic(n, p, N, P)
        statistics.append(cur_stat)
        if cur_stat > max_likelihood:
            max_likelihood = cur_stat

    if verbose:
        print("range", np.amin(statistics), np.amax(statistics))
        print("max likelihood", max_likelihood)
        # n, p, _ = get_simple_stats(regions[idx]["points"], types)
        compute_statistic(n, p, N, P, verbose=verbose)

    return max_likelihood, statistics


def scan_alt_worlds(n_alt_worlds, regions, N, P, seed=None, verbose=False):
    """
    Scans multiple alternative worlds and ranks them by maximum likelihood.

    Args:
        n_alt_worlds (int): Number of alternative worlds to generate.
        regions (list): List of regions.
        N (int): Total number of elements.
        P (int): Total number of positive elements.
        seed (int, optional): Seed for reproducibility. Defaults to None.
        verbose (bool, optional): If True, prints additional information. Defaults to False.

    Returns:
        tuple: A list of alternative worlds sorted by likelihood and the highest likelihood value.
    """

    alt_worlds = []
    current_seed = seed

    for _ in range(n_alt_worlds):
        alt_types = get_random_types(N, P, current_seed)
        cur_P = np.sum(alt_types)
        alt_max_likeli, _ = scan_regions(regions, alt_types, N, cur_P, verbose=verbose)
        alt_worlds.append((alt_types, alt_max_likeli))

        if current_seed is not None:
            current_seed += 1

    alt_worlds.sort(key=lambda x: -x[1])

    return alt_worlds


def get_signif_threshold(
    signif_level, n_alt_worlds, regions, N, P, seed=None, verbose=False
):
    """
    Computes the significance threshold based on alternative worlds.

    Args:
        signif_level (float): Significance level (e.g., 0.05 for 5% significance).
        n_alt_worlds (int): Number of alternative worlds to generate.
        regions (list): List of regions.
        N (int): Total number of elements.
        P (int): Total number of positive elements.
        seed (int, optional): Seed for reproducibility. Defaults to None.
        verbose (bool, optional): If True, prints additional information. Defaults to False.

    Returns:
        float: The computed significance threshold.
    """

    alt_worlds = scan_alt_worlds(n_alt_worlds, regions, N, P, seed, verbose)

    k = int(signif_level * n_alt_worlds)

    signif_thresh = alt_worlds[k][1]  ## get the max likelihood at position k

    return signif_thresh


def get_signif_thresh_scanned_regions(
    signif_level, n_alt_worlds, regions, y_pred, y_true=None, seed=None
):

    if y_true is not None:
        assert len(y_pred) == len(y_true), "y_pred and y_true must have the same length"

        y_pred_pos_indices, regions = get_pos_info_regions(y_true, regions)
        y_pred = y_pred[y_pred_pos_indices]

    N, P = len(y_pred), np.sum(y_pred)
    signif_thresh = get_signif_threshold(
        signif_level, n_alt_worlds, regions, N, P, seed
    )

    _, statistics = scan_regions(regions, y_pred, N, P, verbose=False)

    scanned_regions = []
    for i in range(len(regions)):
        signif = False
        if statistics[i] >= signif_thresh:
            signif = True

        reg = {
            "signif": signif,
            "statistic": statistics[i],
        }
        scanned_regions.append(reg)

    df_scanned_regs = pd.DataFrame(scanned_regions)

    return df_scanned_regs, signif_thresh
