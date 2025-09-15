import io
import base64
import folium
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import colors
import matplotlib.patheffects as pe
import matplotlib.lines as mlines
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def generate_fairness_map_html(
    polygons,
    init_scores,
    norm_scores,
    signif_indices,
    title="",
    center_loc=[34.067133814231646, -118.26273042624089],
    zoom_start=9,
):
    """
    Plots polygon-shaped regions on an interactive Folium map,
    color-coded by a fairness score.

    Args:
        center_loc (list, optional): Latitude and longitude of the map center.
        regs_df_list (list of pandas.DataFrame):
            List of DataFrames. Each DataFrame must have:
              - a 'polygon' column: polygon boundaries as a list of (longitude, latitude) tuples
              - a score column named `score_label`: numeric fairness scores between -1 and 1
        title (str, optional): Title for the Folium map.
        score_label (str, optional): Name of the column holding the fairness score (-1 to 1).

    Returns:
        folium.Map: Folium map object with polygons added.
    """
    # Define colormap from -1 (blue) to +1 (red) with 0 (white) in the middle.
    # cmap = cm.get_cmap("coolwarm")
    cmap = cm.get_cmap("RdBu_r")

    norm = colors.Normalize(vmin=-1, vmax=1)

    # mapit = folium.Map(
    #     location=center_loc,
    #     zoom_start=10,
    # )

    mapit = folium.Map(
        location=center_loc,
        zoom_start=zoom_start,
        # width="100%",  # responsive width
        # height="600%",  # force height
    )

    for i in range(len(polygons)):
        if i in signif_indices:
            continue

        poly = polygons[i]
        score = norm_scores[i]
        init_score = init_scores[i]

        if poly is None or score is None:
            continue

        rgba_color = cmap(norm(score))
        hex_color = colors.to_hex(rgba_color)

        folium.Polygon(
            locations=[(lat, lon) for lon, lat in poly],
            color="black",
            fill=True,
            fill_opacity=0.9,
            fill_color=hex_color,
            weight=3,
            tooltip=(
                f"Id: {i}, SBIr: {init_score:.2f}, SBIr (Normalized): {score:.2f}"
            ),
        ).add_to(mapit)

    for i in signif_indices:
        poly = polygons[i]
        score = norm_scores[i]
        init_score = init_scores[i]
        if poly is None or score is None:
            continue

        rgba_color = cmap(norm(score))
        hex_color = colors.to_hex(rgba_color)

        folium.Polygon(
            locations=[(lat, lon) for lon, lat in poly],
            color="red",
            fill=True,
            fill_opacity=0.9,
            fill_color=hex_color,
            weight=2,
            tooltip=(
                f"Id: {i}, SBIr: {init_score:.2f}, SBIr (Normalized): {score:.2f}"
            ),
        ).add_to(mapit)

    if title:
        title_html = f"""
        <h3 align="center" style="font-size:20px"><b>{title}</b></h3>
        """
        mapit.get_root().html.add_child(folium.Element(title_html))

    # fig, ax = plt.subplots(figsize=(5, 1.2))
    fig, ax = plt.subplots(figsize=(4, 0.4))
    fig.subplots_adjust(bottom=0.4, top=0.9, left=0.05, right=0.95)

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = plt.colorbar(sm, cax=ax, orientation="horizontal")

    fair_band = 0.2

    cb.set_ticks([-1, 0, 1])
    cb.set_ticklabels(["Unfavored", "Fair", "Favored"], fontsize=16)

    cb.ax.vlines([-fair_band, fair_band], *cb.ax.get_ylim(), lw=1)

    ax_top = cb.ax.twiny()
    ax_top.set_xlim(cb.ax.get_xlim())
    ax_top.set_xticks([-1, -fair_band, fair_band, 1])
    min_fair_band_label = f"-{fair_band:.1f}"
    max_fair_band_label = f"+{fair_band:.1f}"
    ax_top.set_xticklabels(["-1", min_fair_band_label, max_fair_band_label, "+1"])
    ax_top.tick_params(axis="x", labelsize=14, pad=1)

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight", transparent=True)
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.read()).decode("utf-8")

    legend_html = f"""
        <div style="
            position: fixed;
            top: 10px; right: 10px;
            z-index:9999;
            width: 300px;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 5px;
            padding: 8px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            text-align: center;
            font-size:14px;
        ">
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 4px;">
                <div style="width: 15px; height: 15px; background-color: transparent; border: 2px solid red;"></div>
                <span style="font-size: 13px;">Significant Bias</span>
            </div>
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; margin-top: 2px;">
        </div>
    """

    mapit.get_root().html.add_child(folium.Element(legend_html))

    css = f"""
    <style>
        .leaflet-tile {{
            filter: brightness({0.5:.2f});
        }}
    </style>
    """
    mapit.get_root().html.add_child(folium.Element(css))

    return mapit.get_root().render()


def generate_threshold_chart_base64(
    thresholds,
    region_sizes,
    figsize=(10, 6),
    display_title=True,
    title="Classification Thresholds per Region",
):
    """
    Plots classification threshold adjustments for different regions.

    This function visualizes classification thresholds across various regions using
    a bar chart. The bars are color-coded based on region sizes using a colormap,
    helping to indicate relative fairness levels.

    Args:
        thresholds (list of float): A list of classification thresholds for each region.
        region_sizes (list of float): A list of region sizes used to determine the bar colors.
        figsize (tuple, optional): Figure size for the plot. Defaults to (10, 6).
        display_title (bool, optional): Whether to display the plot title. Defaults to True.
        title (str, optional): Title of the plot. Defaults to "Classification Thresholds per Region".
    """

    fig, ax = plt.subplots(figsize=figsize)
    x_indices = np.arange(len(thresholds))
    bar_width = 0.6
    cmap = cm.get_cmap("RdBu_r")
    norm = mcolors.Normalize(vmin=-1, vmax=1)

    for i, (thresh, size) in enumerate(zip(thresholds, region_sizes)):
        bar_color = cmap(norm(size))
        ax.bar(
            x_indices[i],
            thresh,
            width=bar_width,
            color=bar_color,
            edgecolor="black",
            alpha=0.85,
        )

    ax.set_xticks(x_indices)
    ax.set_xticklabels([])
    ax.tick_params(axis="both", labelsize=16)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Classification Threshold", fontsize=16)
    ax.set_xlabel("Regions", fontsize=16)

    if display_title:
        ax.set_title(title, fontsize=16, fontweight="bold")

    plt.grid(axis="y", linestyle="--", alpha=0.6)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cb = plt.colorbar(
        sm, ax=ax, aspect=60, pad=0.12, fraction=0.05, orientation="horizontal"
    )  # 👈 Increase `fraction`

    fair_band = 0.2

    cb.set_ticks([-1, 0, 1])
    cb.set_ticklabels(["Unfavored", "Fair", "Favored"], fontsize=16)

    cb.ax.vlines([-fair_band, fair_band], *cb.ax.get_ylim(), lw=1)

    ax_top = cb.ax.twiny()
    ax_top.set_xlim(cb.ax.get_xlim())
    ax_top.set_xticks([-1, -fair_band, fair_band, 1])
    min_fair_band_label = f"-{fair_band:.1f}"
    max_fair_band_label = f"+{fair_band:.1f}"
    ax_top.set_xticklabels(["-1", min_fair_band_label, max_fair_band_label, "+1"])
    ax_top.tick_params(axis="x", labelsize=14, pad=1)

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    plt.close()
    img.seek(0)
    return "data:image/png;base64," + base64.b64encode(img.read()).decode("utf-8")


def generate_distribution_map(
    indiv_info=[],  # List of (lot, lat, y_pred)
    polygons=[],
    flips_info=[],  # (lot, lat, dir)
    regions_pr=[],
    title="",
    center_loc=[34.067133814231646, -118.26273042624089],
    zoom_start=9,
    pts_radius=0.2,
    tp=True,
):

    mapit = folium.Map(
        location=center_loc,
        zoom_start=zoom_start,
    )
    if indiv_info:
        # Add points
        shuffled_indices = np.random.permutation(list(range(len(indiv_info))))
        for idx in shuffled_indices:
            indiv = indiv_info[idx]
            color = "darkgreen" if indiv["pred"] == 1 else "#FF0000"
            folium.CircleMarker(
                location=(indiv["lat"], indiv["lon"]),
                color=color,
                fill_color=color,
                fill=True,
                opacity=1.0,
                fill_opacity=0.8,
                radius=pts_radius,  # if y_pred[index] == 1 else 0.4,
                weight=1.5,  # if y_pred[index] == 1 else 0.2,
            ).add_to(mapit)

    if flips_info:
        shuffled_indices = np.random.permutation(list(range(len(flips_info))))
        for idx in shuffled_indices:
            flip = flips_info[idx]
            color = "orange" if flip["dir"] == -1 else "lightgreen"
            folium.CircleMarker(
                location=(flip["lat"], flip["lon"]),
                color=color,
                fill_color=color,
                fill=True,
                opacity=1.0,
                fill_opacity=0.8,
                radius=pts_radius,
                weight=1.5,
            ).add_to(mapit)

    if polygons:
        pr_label = "True Positive Rate" if tp else "Positive Rate"
        for i, poly in enumerate(polygons):
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in poly],
                color="black",
                fill=True,
                fill_color="#0000FF",
                fill_opacity=0,
                weight=2,
                tooltip=(
                    f"Id: {i}, {pr_label}: {regions_pr[i]:.2f}" if regions_pr else ""
                ),
            ).add_to(mapit)

    if title:
        title_html = f"""
        <h3 align="center" style="font-size:20px"><b>{title}</b></h3>
        """
        mapit.get_root().html.add_child(folium.Element(title_html))

    legend_items = []

    pos_label = "True Positive" if tp else "Positive"
    neg_label = "False Negative" if tp else "Negative"
    circle = (
        lambda color: f'<span style="display:inline-block;width:12px;height:12px;background:{color};border-radius:50%;margin-right:6px;"></span>'
    )

    if indiv_info:
        legend_items.append(f'{circle("darkgreen")}{pos_label}')
        legend_items.append(f'{circle("#FF0000")}{neg_label}')

    if flips_info:
        legend_items.append(f'{circle("orange")}Flip to Negative')
        legend_items.append(f'{circle("lightgreen")}Flip to Positive')

    if legend_items:
        legend_html = f"""
        <div style="
            position: fixed;
            top: 10px;  /* <--- Moved to top */
            right: 10px;
            z-index: 9999;
            background-color: rgba(255, 255, 255, 0.7);
            padding: 8px 12px;
            border-radius: 6px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            font-size: 13px;
            line-height: 1.4em;
        ">
            {'<br>'.join(legend_items)}
        </div>
        """
        mapit.get_root().html.add_child(folium.Element(legend_html))

    css = f"""
    <style>
        .leaflet-tile {{
            filter: brightness({0.5:.2f});
        }}
    </style>
    """
    mapit.get_root().html.add_child(folium.Element(css))

    return mapit.get_root().render()


def generate_synthetic_distribution_plot(
    layout, pts_per_region, xaxis_limits, yaxis_limits, tp=True
):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    indivs_layout = layout["individuals"]
    regions_layout = layout["regions"]
    pos_label = "True Positive" if tp else "Positive"
    neg_label = "False Negative" if tp else "Negative"

    # 1) one dynamic markersize for all points
    ms_global = layout["global_ms"]

    # 2) compute raw spans from regions (before padding)
    xs, ys = [], []
    for reg in regions_layout.values():
        (cx, cy), R = reg["center"], reg["radius"]
        xs.extend([cx - R, cx + R])
        ys.extend([cy - R, cy + R])

    # 3) draw FILLED regions under points
    for region_layout in regions_layout.values():
        radius = region_layout["radius"]
        center = region_layout["center"]
        ax.add_patch(
            plt.Circle(
                center,
                radius=radius,
                facecolor="white",
                alpha=1.0,
                ec="none",
                lw=0,
                zorder=1,
            )
        )

    # 4) plot points
    for region_id, region_layout in regions_layout.items():
        pts = pts_per_region[region_id]
        if not pts:
            continue
        xs = [indivs_layout[p]["x"] for p in pts]
        ys = [indivs_layout[p]["y"] for p in pts]
        cols = [
            "#FF0000" if indivs_layout[p]["y_pred"] == 0 else "darkgreen" for p in pts
        ]
        for x, y, c in zip(xs, ys, cols):
            ax.plot(x, y, "o", color=c, markersize=ms_global, zorder=2, clip_on=False)

    # 5) draw borders on top
    for region_layout in regions_layout.values():
        radius = region_layout["radius"]
        center = region_layout["center"]
        border = plt.Circle(
            center, radius=radius, fill=False, ec="black", lw=2.0, zorder=4
        )
        border.set_path_effects(
            [
                pe.Stroke(linewidth=3.8, foreground="white"),
                pe.Normal(),
            ]
        )
        ax.add_patch(border)

    ax.set_xlim(xaxis_limits)
    ax.set_ylim(yaxis_limits)

    ax.axis("off")
    fig.tight_layout()

    # --- 7) add legend ---
    red_proxy = mlines.Line2D(
        [],
        [],
        color="#FF0000",
        marker="o",
        linestyle="None",
        markersize=ms_global,
        label=neg_label,
    )
    green_proxy = mlines.Line2D(
        [],
        [],
        color="darkgreen",
        marker="o",
        linestyle="None",
        markersize=ms_global,
        label=pos_label,
    )
    ax.legend(
        handles=[red_proxy, green_proxy],
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="black",
        framealpha=0.7,
        fontsize=16,
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"


def generate_synthetic_flips_distribution_plot(
    layout,
    pts_per_region,
    xaxis_limits,
    yaxis_limits,
):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    indivs_layout = layout["individuals"]
    regions_layout = layout["regions"]

    # One dynamic marker size for ALL points (fallback if not stored in layout)
    ms_global = layout["global_ms"]

    # --- compute raw spans from regions (before padding) ---
    xs_edges, ys_edges = [], []
    for reg in regions_layout.values():
        (cx, cy), R = reg["center"], reg["radius"]
        xs_edges.extend([cx - R, cx + R])
        ys_edges.extend([cy - R, cy + R])
    x_min_raw, x_max_raw = (min(xs_edges), max(xs_edges)) if xs_edges else (-1, 1)
    y_min_raw, y_max_raw = (min(ys_edges), max(ys_edges)) if ys_edges else (-1, 1)
    x_span_raw = max(x_max_raw - x_min_raw, 1e-6)
    y_span_raw = max(y_max_raw - y_min_raw, 1e-6)

    # --- FILLED regions under points ---
    for region_layout in regions_layout.values():
        radius = region_layout["radius"]
        center = region_layout["center"]
        disk = plt.Circle(
            center,
            radius=radius,
            facecolor="white",
            alpha=1.0,
            ec="none",
            lw=0,
            zorder=1,
        )
        disk.set_clip_on(False)
        ax.add_patch(disk)

    # --- POINTS ---
    if isinstance(pts_per_region, dict):
        region_ids = regions_layout.keys()
        get_pts = lambda rid: pts_per_region.get(rid, [])
    else:
        region_ids = range(len(pts_per_region))
        get_pts = lambda rid: pts_per_region[rid]

    for rid in region_ids:
        pts = get_pts(rid)
        if not pts:
            continue
        xs = [indivs_layout[p]["x"] for p in pts]
        ys = [indivs_layout[p]["y"] for p in pts]
        cols = [
            "lightgreen" if indivs_layout[p]["y_pred"] == 0 else "orange" for p in pts
        ]
        ax.scatter(
            xs, ys, s=ms_global**2, c=cols, zorder=2, linewidths=0, clip_on=False
        )

    # --- BORDERS ---
    for region_layout in regions_layout.values():
        radius = region_layout["radius"]
        center = region_layout["center"]
        border = plt.Circle(
            center, radius=radius, fill=False, ec="black", lw=2.0, zorder=4
        )
        border.set_path_effects(
            [pe.Stroke(linewidth=3.8, foreground="white"), pe.Normal()]
        )
        border.set_clip_on(False)
        ax.add_patch(border)

    ax.set_xlim(xaxis_limits)
    ax.set_ylim(yaxis_limits)

    ax.axis("off")
    fig.tight_layout()

    # --- LEGEND ---
    neg_proxy = mlines.Line2D(
        [],
        [],
        color="orange",
        marker="o",
        linestyle="None",
        markersize=ms_global,
        label="Flips to Negative",
    )
    pos_proxy = mlines.Line2D(
        [],
        [],
        color="lightgreen",
        marker="o",
        linestyle="None",
        markersize=ms_global,
        label="Flips to Positive",
    )
    ax.legend(
        handles=[neg_proxy, pos_proxy],
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="black",
        framealpha=0.8,
        fontsize=16,
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"


def generate_synthetic_fairness_map_plot(
    scores, signif_indices, regions_layout, xaxis_limits, yaxis_limits
):

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")

    norm = mcolors.Normalize(vmin=-1, vmax=1)
    cmap = cm.get_cmap("RdBu_r")

    for region_id in range(len(scores)):
        score = scores[region_id]
        rgba = cmap(norm(score))
        color = mcolors.to_hex(rgba)
        is_signif = region_id in signif_indices
        region_layout = regions_layout[region_id]
        radius = region_layout["radius"]
        center = region_layout["center"]

        circle = plt.Circle(
            center,
            radius=radius,
            color=color,
            alpha=0.9,
            ec="red" if is_signif else "black",
            lw=2,
            zorder=1,
        )
        ax.add_patch(circle)

    ax.set_xlim(xaxis_limits)
    ax.set_ylim(yaxis_limits)

    ax.axis("off")

    fair_band = 0.2  # τ

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)

    sm.set_array([])
    cax = inset_axes(ax, width="70%", height="3%", loc="lower center", borderpad=2.2)
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")

    # sm.set_array(np.linspace(-1, 1, 256))  # ensure gradient renders

    # cb = fig.colorbar(
    #     sm,
    #     ax=ax,
    #     orientation="horizontal",
    #     fraction=0.046,  # thickness ~ 4.6% of ax width (tweak as needed)
    #     pad=0.08,  # gap between ax and bar (increase if labels clip)
    #     aspect=30,  # controls length/thickness ratio
    # )

    cb.set_ticks([-1, 0, 1])
    cb.set_ticklabels(["Unfavored", "Fair", "Favored"])
    cb.ax.tick_params(labelsize=16, pad=2)  # pad pulls labels closer to the bar

    cb.ax.vlines([-fair_band, fair_band], *cb.ax.get_ylim(), lw=1, alpha=0.85)
    ax_top = cb.ax.twiny()
    ax_top.set_xlim(cb.ax.get_xlim())
    ax_top.set_xticks([-1, -fair_band, fair_band, 1])
    ax_top.set_xticklabels(["-1", f"-{fair_band:g}", f"+{fair_band:g}", "+1"])
    ax_top.tick_params(axis="x", labelsize=14, pad=1)

    # Legend for significance (edge color encodes significance)
    sig_handle = Line2D(
        [],
        [],
        marker="o",
        linestyle="None",
        markerfacecolor="none",
        markeredgecolor="red",
        markeredgewidth=2,
        markersize=14,
        label="Significant bias",
    )

    ax.legend(
        handles=[sig_handle],
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="black",
        framealpha=0.8,
        fontsize=16,
    )

    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
