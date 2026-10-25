import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt

# PDF / EPS font settings
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42


# Configuration
CONFIG = {
    "figure": {"figsize": (8, 5)},
    "font": {
        "family": "DejaVu Sans",
        "label": 16,
        "ticks": 12,
    },
    "axes": {
        "xlabel": "Sample Index",
        "ylabel": "Value",
    },
    "line": {"width": 2.0},
    "marker": {
        "size": 8,
        "edge_width": 1.8,
        "face_color": "none",  # transparent even when lines overlap
    },
    "legend": {
        # Add/remove/reorder names to control which curves are displayed.
        "labels": ["Method A", "Method B", "Method C", "Method D", "Method E",
                   "Method F", "Method G", "Method H", "Method I", "Ours"],
        "show": True,
        "fontsize": 16,
        "loc": "separate",  # best, lower left, upper right, separate, ...
        "frameon": True,
        "ncol": 2,
    },
    "grid": {"show": True, "alpha": 0.2},
    "ours": {
        "label": "Ours",
        "color": "#E94849",  # reserved red; never assigned to other methods
        "marker": "s",
        "linestyle": "-",
        "zorder": 10,
    },
}

COLORS = [
    "#5D93BF", "#71BF6E", "#FF9933", "#AD71B5", "#24A6A3",
    "#C6A13C", "#D66D9C", "#96765C", "#697C90",
]
MARKERS = ["o", "^", "D", "v", "P", "X", "<", ">", "H"]
LINESTYLES = [
    "-", "--", "-.", ":", (0, (5, 2)), (0, (3, 1, 1, 1)),
    (0, (1, 1)), (0, (7, 2)), (0, (5, 2, 1, 2)),
]


# Sample data (replace this dictionary with actual results)
x = np.arange(11)

labels = CONFIG["legend"]["labels"]
ours_label = CONFIG["ours"]["label"]

other_labels = [name for name in labels if name != ours_label]

DATA = {
    name: 1 + i * 0.58 + 0.24 * np.sin(x * 0.66 + i * 0.45) + 0.035 * x
    for i, name in enumerate(other_labels)
}

if ours_label in labels:
    DATA[ours_label] = (
        3.7 + 0.24 * np.sin(x * 0.66 + 2.1) + 0.035 * x
    )


# Plot
labels = CONFIG["legend"]["labels"]
ours_label = CONFIG["ours"]["label"]

if len(labels) != len(set(labels)):
    raise ValueError("Legend labels must be unique.")

missing = [name for name in labels if name not in DATA]
if missing:
    raise ValueError(f"Missing data for legend labels: {missing}")

other_labels = [name for name in labels if name != ours_label]
if len(other_labels) > min(len(COLORS), len(MARKERS), len(LINESTYLES)):
    raise ValueError("Too many competing methods for the available styles (maximum 9).")

mpl.rcParams["font.family"] = CONFIG["font"]["family"]
fig, ax = plt.subplots(figsize=CONFIG["figure"]["figsize"])

for i, name in enumerate(other_labels):
    ax.plot(
        x, DATA[name],
        label=name,
        color=COLORS[i],
        linestyle=LINESTYLES[i],
        linewidth=CONFIG["line"]["width"],
        marker=MARKERS[i],
        markersize=CONFIG["marker"]["size"],
        markerfacecolor=CONFIG["marker"]["face_color"],
        markeredgecolor=COLORS[i],
        markeredgewidth=CONFIG["marker"]["edge_width"],
        zorder=2,
    )

# Ours is always drawn last, independently of its position in legend labels.
if ours_label in labels:
    ours = CONFIG["ours"]
    ax.plot(
        x, DATA[ours_label],
        label=ours_label,
        color=ours["color"],
        linestyle=ours["linestyle"],
        linewidth=CONFIG["line"]["width"],
        marker=ours["marker"],
        markersize=CONFIG["marker"]["size"],
        markerfacecolor=CONFIG["marker"]["face_color"],
        markeredgecolor=ours["color"],
        markeredgewidth=CONFIG["marker"]["edge_width"],
        zorder=ours["zorder"],
    )

ax.set_xlabel(CONFIG["axes"]["xlabel"], fontsize=CONFIG["font"]["label"])
ax.set_ylabel(CONFIG["axes"]["ylabel"], fontsize=CONFIG["font"]["label"])
ax.tick_params(axis="both", labelsize=CONFIG["font"]["ticks"])

if CONFIG["grid"]["show"]:
    ax.grid(alpha=CONFIG["grid"]["alpha"])

if CONFIG["legend"]["show"]:
    handles, drawn_labels = ax.get_legend_handles_labels()
    by_label = dict(zip(drawn_labels, handles))
    legend_config = CONFIG["legend"]

    ordered_handles = [by_label[name] for name in labels]

    if legend_config["loc"] == "separate":
        # Legend-only figure, sized to fit the legend
        legend_fig = plt.figure()
        leg = legend_fig.legend(
            ordered_handles,
            labels,
            fontsize=legend_config["fontsize"],
            loc="center",
            frameon=legend_config["frameon"],
            ncol=legend_config["ncol"],
        )

        # Measure legend size (inches) and shrink the figure to it
        legend_fig.canvas.draw()
        bbox = leg.get_window_extent().transformed(
            legend_fig.dpi_scale_trans.inverted()
        )
        pad = 0.05  # inches; prevents clipping the frame line
        legend_fig.set_size_inches(bbox.width + 2 * pad, bbox.height + 2 * pad)

    else:
        # Draw legend inside the original figure
        ax.legend(
            ordered_handles,
            labels,
            fontsize=legend_config["fontsize"],
            loc=legend_config["loc"],
            frameon=legend_config["frameon"],
            ncol=legend_config["ncol"],
        )

fig.tight_layout()
plt.show()
