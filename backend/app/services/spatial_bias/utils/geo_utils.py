from sklearn.cluster import KMeans
from rtree import index
from shapely.geometry import MultiPoint
from sklearn.cluster import MiniBatchKMeans
import numpy as np
from collections import Counter
from sklearn.metrics import silhouette_score
from typing import List
import random
from shapely.geometry import Polygon, Point


def create_rtree(df):
    """
    Creates an R-tree spatial index for efficient querying of spatial points.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns representing longitude and latitude.

    Returns:
        rtree.Index: An R-tree spatial index for the points in the DataFrame.
    """

    rtree = index.Index()

    for idx, row in df.iterrows():
        left, bottom, right, top = row["lon"], row["lat"], row["lon"], row["lat"]
        rtree.insert(idx, (left, bottom, right, top))

    return rtree


def filterbbox(df, min_lon, min_lat, max_lon, max_lat):
    """
    Filters the DataFrame to include only points within a specified bounding box.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns representing longitude and latitude.
        min_lon (float): Minimum longitude of the bounding box.
        min_lat (float): Minimum latitude of the bounding box.
        max_lon (float): Maximum longitude of the bounding box.
        max_lat (float): Maximum latitude of the bounding box.

    Returns:
        pd.DataFrame: A DataFrame containing points within the bounding box.
    """

    df = df.loc[df["lon"] >= min_lon]
    df = df.loc[df["lon"] <= max_lon]
    df = df.loc[df["lat"] >= min_lat]
    df = df.loc[df["lat"] <= max_lat]
    # df.reset_index(drop=True, inplace=True)

    return df


def create_seeds(df, rtree, n_seeds, rand_seed=None):
    """
    Uses K-means clustering to create seed points from clusters of geographical points.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        rtree (rtree.Index): An R-tree spatial index for efficient querying.
        n_seeds (int): Number of seeds (clusters) to generate.
        rand_seed (int, optional): Random seed for reproducibility.

    Returns:
        list: A list of indices representing seed points.
    """

    # Compute clusters with k-means
    X = df[["lon", "lat"]].to_numpy()
    kmeans = KMeans(n_clusters=n_seeds, n_init="auto", random_state=rand_seed).fit(X)
    cluster_centers = kmeans.cluster_centers_

    # Pick seeds from cluster centroids
    seeds = []
    for c in cluster_centers:
        nearest_idx = list(rtree.nearest([c[0], c[1]], 1))[0]
        lat = df.loc[[nearest_idx]]["lat"].values[0]
        lon = df.loc[[nearest_idx]]["lon"].values[0]
        seeds.append((lat, lon))
    return seeds


def create_non_over_regions(df, n_seeds, rand_seed=None):
    """
    Uses K-means clustering to create n_seeds regions with non-overlapping points.
    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        n_seeds (int): Number of seeds (clusters) to generate.
        rand_seed (int, optional): Random seed for reproducibility.

    Returns:
        list: A list of indices representing seed points.
    """

    # Compute clusters with k-means
    X = df[["lon", "lat"]].to_numpy()
    kmeans = KMeans(n_clusters=n_seeds, n_init="auto", random_state=rand_seed).fit(X)
    regions = []
    for seed in range(n_seeds):
        points = df.index[kmeans.labels_ == seed].tolist()
        region = {
            "points": points,
            "center": seed,
        }
        regions.append(region)

    return regions


def query_range(rtree, center_lat, center_lon, radius):
    """
    Queries points within a square bounding box centered at a specific point.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        rtree (rtree.Index): An R-tree spatial index for efficient querying.
        center (int): Index of the center point in the DataFrame.
        radius (float): Radius of the square bounding box to query.

    Returns:
        list: List of indices of points within the square bounding box.
    """

    ## for now returns points within square

    left, bottom, right, top = (
        center_lon - radius,
        center_lat - radius,
        center_lon + radius,
        center_lat + radius,
    )
    result = list(rtree.intersection((left, bottom, right, top)))
    # keep points that are in circle
    # tmp_result = []
    # for point in result:
    #     p_lat, p_lon = id2loc(df, point)
    #     dist = math.sqrt( (p_lon-lon)**2 + (p_lat-lat)**2 )
    #     if dist <= radius:
    #         tmp_result.append(point)
    # result = tmp_result

    return result


def create_regions(rtree, seeds, radii):
    """
    Creates regions around seed points with varying radii.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        rtree (rtree.Index): An R-tree spatial index for efficient querying.
        seeds (list): List of seed point indices.
        radii (list): List of radii for each region.

    Returns:
        list: List of dictionaries, each representing a region with 'points', 'center', and 'radius'.
    """

    regions = []
    for lat, lon in seeds:
        for radius in radii:
            points = query_range(rtree, lat, lon, radius)
            region = {
                "points": points,
                "center_lat": lat,
                "center_lon": lon,
                "radius": radius,
            }
            regions.append(region)

    return regions


def query_range_box(rtree, xmin, xmax, ymin, ymax):
    """
    Queries points within a rectangular bounding box.

    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        rtree (rtree.Index): An R-tree spatial index for efficient querying.
        xmin (float): Minimum longitude of the bounding box.
        xmax (float): Maximum longitude of the bounding box.
        ymin (float): Minimum latitude of the bounding box.
        ymax (float): Maximum latitude of the bounding box.

    Returns:
        list: List of indices of points within the bounding box.
    """

    left, bottom, right, top = xmin, ymin, xmax, ymax
    result = list(rtree.intersection((left, bottom, right, top)))

    return result


def create_non_over_regions(df, n_seeds, rand_seed=None):
    """
    Uses K-means clustering to create n_seeds regions with non-overlapping points.
    Args:
        df (pd.DataFrame): DataFrame containing 'lon' and 'lat' columns.
        n_seeds (int): Number of seeds (clusters) to generate.
        rand_seed (int, optional): Random seed for reproducibility.

    Returns:
        list: A list of indices representing seed points.
    """

    # Compute clusters with k-means
    X = df[["lon", "lat"]].to_numpy()
    kmeans = KMeans(n_clusters=n_seeds, n_init="auto", random_state=rand_seed).fit(X)
    cluster_centers = kmeans.cluster_centers_

    regions = []
    for idx, center in enumerate(cluster_centers):
        points = df.index[kmeans.labels_ == idx].tolist()
        region = {
            "points": points,
            "center_lat": center[1],
            "center_lon": center[0],
        }
        regions.append(region)

    return regions


def compute_polygons(regions_df, df_points):
    """
    Computes convex hull polygons for each region using Shapely.

    Args:
        regions_df (pd.DataFrame): DataFrame containing 'center_lat', 'center_lon', and 'points' columns.
        df_points (pd.DataFrame): DataFrame containing 'lat' and 'lon' columns for points.

    Returns:
        pd.DataFrame: Updated regions_df with new 'polygon' column.
    """
    polygons = []

    for _, row in regions_df.iterrows():
        points = row["points"]

        if not points:
            polygons.append(None)
            continue

        # Get coordinates of points in the region
        region_points = df_points.iloc[points][["lon", "lat"]].values

        # Compute the convex hull (polygon boundary)
        hull = MultiPoint(region_points).convex_hull
        polygons.append(
            list(hull.exterior.coords) if hull.geom_type == "Polygon" else None
        )

    regions_df["polygon"] = polygons
    return regions_df


def get_points_not_covered(df, regions):
    """
    Identifies points that are not covered by any region.

    Args:
        df (pd.DataFrame): Dataframe containing all points.
        regions (list): List of region dictionaries, each containing "points".

    Returns:
        list: List of point indices that are not covered by any region.
    """

    covered_points = set()

    for region in regions:
        for point in region["points"]:
            covered_points.add(point)

    all_points = set(df.index)
    missing_points = all_points - covered_points

    return list(missing_points)


# def compute_optimal_radius(n_points, zoom=9):
#     """
#     Dynamically computes a suitable point radius for folium.CircleMarker
#     based on the number of points and optional map zoom level.

#     Args:
#         n_points (int): Total number of points to plot.
#         zoom (int): Folium zoom level (default 9).

#     Returns:
#         float: A radius value suitable for CircleMarker.
#     """
#     if n_points == 0:
#         return 0.2  # fallback

#     base_radius = 5  # max radius in pixels
#     scale = max(n_points / 500, 1)  # scale down when > 500
#     radius = base_radius / scale

#     # Clamp radius to a reasonable range
#     return max(0.4, min(radius, 5))


def compute_optimal_radius(n_points: int, zoom: int = 9) -> float:
    """
    Computes a suitable radius for folium.CircleMarker points based on the number
    of points and the map zoom level.

    Args:
        n_points (int): Number of points to plot.
        zoom (int): Zoom level of the folium map (higher = more zoomed in).

    Returns:
        float: An optimal radius value.
    """
    if n_points == 0:
        return 0.2  # fallback value

    # Base radius: higher zoom → can afford larger points
    zoom_factor = (18 - zoom) / 9  # normalize: 0 at zoom=18, 1 at zoom=9
    base_radius = 4.0 + zoom_factor * 2.0  # e.g., 6 at zoom=9, 4 at zoom=18

    # Adjust based on number of points
    point_scale = max(n_points / 500, 1)  # shrink if too many points
    radius = base_radius / point_scale

    return max(0.3, min(radius, 6.0))  # clamp radius


def compute_map_info(polygons, max_zoom=16, min_zoom=4):
    lats = []
    lons = []
    min_lon, max_lon, min_lat, max_lat = (
        float("inf"),
        float("-inf"),
        float("inf"),
        float("-inf"),
    )
    for polygon in polygons:
        for lon, lat in polygon:
            lats.append(lat)
            lons.append(lon)
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)
            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)

    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Estimate zoom level based on lat/lon span
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon
    span = max(lat_span, lon_span)

    # Approximate zoom level formula (empirical)
    if span < 0.005:
        zoom = 16
    elif span < 0.01:
        zoom = 15
    elif span < 0.02:
        zoom = 14
    elif span < 0.04:
        zoom = 13
    elif span < 0.08:
        zoom = 12
    elif span < 0.16:
        zoom = 11
    elif span < 0.32:
        zoom = 10
    else:
        zoom = 9

    zoom = max(min_zoom, min(max_zoom, zoom))
    return (center_lat, center_lon), zoom


# def get_optimal_radius(zoom):
#     if zoom >= 15:
#         return 12
#     elif zoom >= 13:
#         return 10
#     elif zoom >= 11:
#         return 8
#     elif zoom >= 9:
#         return 6
#     else:
#         return 4


def compute_radius(zoom):
    return max(4, min(12, int((18 - zoom) * 1.2)))  # shrink radius as you zoom in


def get_regions_ch(pts_per_region, lats, lons):
    polygons = []

    for points in pts_per_region:
        if not points:
            polygons.append(None)
            continue

        # Get coordinates of points in the region
        region_points = [(lons[i], lats[i]) for i in points]

        # Compute the convex hull (polygon boundary)
        hull = MultiPoint(region_points).convex_hull
        polygons.append(
            list(hull.exterior.coords) if hull.geom_type == "Polygon" else None
        )

    return polygons


def spatial_cluster_fast(coords: np.ndarray, random_state: int = 42) -> list[list[int]]:
    N = len(coords)
    k = max(5, int(np.sqrt(N) / 2))
    # print(f"Using fast clustering with k={k} for {N} points")
    model = MiniBatchKMeans(n_clusters=k, random_state=random_state)
    labels = model.fit_predict(coords)

    # Count number of points per cluster
    label_counts = Counter(labels)

    # Remap small clusters (<3 points) to nearest large cluster
    large_clusters = {label for label, count in label_counts.items() if count >= 3}
    small_clusters = {label for label in label_counts if label not in large_clusters}

    if small_clusters:
        large_centroids = model.cluster_centers_[list(large_clusters)]

        for i, label in enumerate(labels):
            if label in small_clusters:
                point = coords[i]
                dists = np.linalg.norm(large_centroids - point, axis=1)
                nearest_large = list(large_clusters)[np.argmin(dists)]
                labels[i] = nearest_large

    return [[int(label)] for label in labels]


def spatial_cluster_auto_k(
    coords: np.ndarray, random_state: int = 42
) -> List[List[int]]:
    N = len(coords)
    max_k = min(15, N // 3)
    best_score = -1
    best_labels = None

    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=random_state)
        labels = model.fit_predict(coords)

        counts = Counter(labels)
        if any(c < 3 for c in counts.values()):
            continue  # Skip if any cluster has fewer than 3 points

        try:
            score = silhouette_score(coords, labels)
            if score > best_score:
                best_score = score
                best_labels = labels
        except Exception:
            continue

    if best_labels is None:
        # fallback to fast method
        from sklearn.cluster import MiniBatchKMeans

        fallback_k = max(5, int(np.sqrt(N) / 2))
        model = MiniBatchKMeans(n_clusters=fallback_k, random_state=random_state)
        best_labels = model.fit_predict(coords)

    return [[int(label)] for label in best_labels]


# from hdbscan import HDBSCAN
# from sklearn.neighbors import NearestCentroid

# def spatial_cluster_hdbscan(coords: np.ndarray, min_cluster_size: int = 3) -> List[List[int]]:
#     model = HDBSCAN(min_cluster_size=min_cluster_size)
#     labels = model.fit_predict(coords)

#     # -1 = noise; we'll reassign it
#     labels = np.array(labels)
#     valid_mask = labels != -1
#     cluster_counts = Counter(labels[valid_mask])

#     # Reassign noise (-1) or small clusters to nearest centroid
#     centroider = NearestCentroid()
#     centroider.fit(coords[valid_mask], labels[valid_mask])

#     for i in range(len(labels)):
#         if labels[i] == -1:
#             labels[i] = centroider.predict(coords[i].reshape(1, -1))[0]

#     return [[int(label)] for label in labels]


from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree
from typing import List


def assign_region_ids_with_strtree(
    coords: List[List[float]], polygons: List[List[List[float]]]
) -> List[List[int]]:
    shapely_polygons = [Polygon(polygon) for polygon in polygons]

    tree = STRtree(shapely_polygons)

    polygon_to_index = {id(p): idx for idx, p in enumerate(shapely_polygons)}

    region_ids = []

    for coord in coords:
        point = Point([coord[1], coord[0]])
        candidate_idxs = tree.query(point)
        found = False
        for idx in candidate_idxs:
            poly = shapely_polygons[idx]
            if poly.contains(point):
                region_ids.append([polygon_to_index[id(poly)]])
                found = True
                break
        if not found:
            region_ids.append([-1])  # fallback if no polygon contains point

    return region_ids


def generate_points_in_polygon(polygon_points, n):
    """
    Generate n uniformly distributed points inside a polygon.

    Args:
        polygon_points (List[List[float]]): List of [lat, lon] points.
        n (int): Number of points to generate.

    Returns:
        List of [lon, lat] points inside the polygon.
    """
    # Fix: Convert [lat, lon] → [lon, lat]
    polygon = Polygon([[pt[1], pt[0]] for pt in polygon_points])
    minx, miny, maxx, maxy = polygon.bounds

    points = []
    attempts = 0
    max_attempts = n * 100

    while len(points) < n and attempts < max_attempts:
        lon = random.uniform(minx, maxx)
        lat = random.uniform(miny, maxy)
        point = Point(lon, lat)
        if polygon.contains(point):
            points.append([lon, lat])
        attempts += 1

    if len(points) < n:
        raise ValueError(
            f"Only generated {len(points)} points after {attempts} attempts."
        )

    return points
