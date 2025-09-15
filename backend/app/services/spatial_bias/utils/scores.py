import numpy as np
import math


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


def compute_statistic_l0_l1(n, p, N, P, verbose=False):
    """
    Computes the test statistic along with l0max and l1max values.

    Args:
        n (int): Number of points in the region.
        p (int): Number of positive labels in the region.
        N (int): Total number of points.
        P (int): Total number of positive labels.
        verbose (bool, optional): If True, prints intermediate steps. Defaults to False.

    Returns:
        tuple: (statistic, l0max, l1max) where `statistic` is l1max - l0max.
    """

    ## l1max - l0max
    if verbose:
        print(f"{n=}, {p=}, {N=}, {P=}")

    if n == 0 or n == N:  ## rho_in == 0/0 or rho_out == 0/0
        print("n == 0 or n == N")
        return 0, 0, 0

    rho = P / N
    rho_in = p / n
    rho_out = (P - p) / (N - n)

    if verbose:
        print(f"{rho=}, {rho_in=}, {rho_out=}")

    if rho == 1 or rho == 0:
        l0max = 0
    else:
        l0max = P * math.log(rho) + (N - P) * math.log(1 - rho)

    l1max = compute_max_likeli(n, p, N, P)
    statistic = l1max - l0max

    # l1max = p*math.log(rho_in) + (n-p)*math.log(1-rho_in) + (P-p)*math.log(rho_out) + (N-n - (P-p))*math.log(1-rho_out)
    # l0max = P*math.log(rho) + (N-P)*math.log(1-rho)

    if verbose:
        print(f"{l0max=}, {l1max=}, {statistic=}")

    return statistic, l0max, l1max


def compute_statistic_with_info(n, p, N, P, verbose=False):
    """
    Computes the test statistic and returns it along with in-region and out-region proportions.

    Args:
        n (int): Number of points in the region.
        p (int): Number of positive labels in the region.
        N (int): Total number of points.
        P (int): Total number of positive labels.
        verbose (bool, optional): If True, prints intermediate steps. Defaults to False.

    Returns:
        tuple: (statistic, rho_in, rho_out) where `statistic` is l1max - l0max, `rho_in` is the in-region proportion, and `rho_out` is the out-region proportion.
    """

    ## l1max - l0max

    if verbose:
        print(f"{n=}, {p=}, {N=}, {P=}")

    rho = P / N
    rho_in = p / n
    rho_out = (P - p) / (N - n)

    if n == 0 or n == N:  ## rho_in == 0/0 or rho_out == 0/0
        if verbose:
            print("n == 0 or n == N")
        return 0, rho_in, rho_out

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

    l1max = compute_max_likeli(n, p, N, P)
    if verbose:
        print(f"{l1max=}")

    statistic = l1max - l0max

    # l1max = p*math.log(rho_in) + (n-p)*math.log(1-rho_in) + (P-p)*math.log(rho_out) + (N-n - (P-p))*math.log(1-rho_out)
    # l0max = P*math.log(rho) + (N-P)*math.log(1-rho)

    if verbose:
        print(f"{l0max=}, {l1max=}, {statistic=}")

    return statistic, rho_in, rho_out


def get_sbi(labels, points_per_region, with_stats=False):
    """
    Computes the Mean Likelihood Ratio (SBI) for a set of regions based on the label distribution.

    Args:
        labels (np.ndarray): Array of binary labels for all points.
        points_per_region (list): List of regions, where each region contains indices of points.

    Returns:
        float: The Mean Likelihood Ratio (SBI) across all regions.
    """

    P = np.sum(labels)
    N = len(labels)
    list_stats = []

    for i in range(len(points_per_region)):
        n = len(points_per_region[i])
        if n == 0:
            continue
        p = np.sum(labels[points_per_region[i]])
        _, l0, l1_i = compute_statistic_l0_l1(n, p, N, P)
        list_stats.append(1 - l1_i / l0)

    sbi = np.mean(list_stats)
    if with_stats:
        return sbi, list_stats

    return sbi


def get_statistics(labels, points_per_region):
    """
    Computes the Mean Likelihood Ratio (SBI) for a set of regions based on the label distribution.

    Args:
        labels (np.ndarray): Array of binary labels for all points.
        points_per_region (list): List of regions, where each region contains indices of points.

    Returns:
        float: The Mean Likelihood Ratio (SBI) across all regions.
    """

    P = np.sum(labels)
    N = len(labels)
    list_stats = []

    for i in range(len(points_per_region)):
        n = len(points_per_region[i])
        if n == 0:
            continue
        p = np.sum(labels[points_per_region[i]])
        stat, _, _ = compute_statistic_l0_l1(n, p, N, P)
        list_stats.append(stat)

    return list_stats


def get_fair_stat_ratios(
    stats, pr_s, PR, t, cap=None, percentile_cap=95, fair_band=0.2
):
    """
    Map unsigned 'stats' to a signed scale in [-1, 1]:
      - If s < t: map to 0 .. ±fair_band (sign by pr_s vs PR), with s=0 -> 0, s=t -> ±fair_band
      - If s ≥ t: map to ±fair_band .. ±1, saturating at ±1 as s → cap
    pr_s > PR => favored (+), else unfavored (−).
    """
    stats = np.asarray(stats, dtype=float)
    pr_s = np.asarray(pr_s, dtype=float)
    dir_sign = np.where(pr_s > PR, 1.0, -1.0)  # + favored, - unfavored

    # Robust saturation cap (avoid outliers & ensure cap > t)
    cap = (
        max(float(t) + 1e-12, float(np.percentile(stats, percentile_cap)))
        if cap is None
        else cap
    )

    out = []
    for s, sign in zip(stats, dir_sign):
        if not np.isfinite(s):
            out.append(0.0)
            continue

        if s < t:
            # Scale 0..t → 0..fair_band, then apply direction
            alpha = 0.0 if t <= 0 else s / t
            val = sign * (fair_band * alpha)  # s=0 -> 0 ; s=t -> ±fair_band
        else:
            # Scale t..cap → fair_band..1, then apply direction
            denom = cap - t
            alpha = 1.0 if denom <= 0 else np.clip((s - t) / denom, 0.0, 1.0)
            edge = fair_band + (1.0 - fair_band) * alpha  # fair_band..1
            val = sign * edge

        out.append(float(val))

    return out, float(cap)
