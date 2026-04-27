import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

from importer import ZONE_NAMES


def vis_acitivty_by_zones(
    zones_activity_a: dict[str, float],
    zones_activity_b: dict[str, float],
    label_a: str = 'A',
    label_b: str = 'B',
    title: str | None = None,
) -> None:
    """Няшный визуализатор активности, написан клавдией чисто для теста данных"""

    COLS, ROWS = 3, 3
    TW, TH = 1.0, 0.7
    GAP = 0.18
    STEP_X = TW + GAP
    STEP_Y = TH + GAP
    CMAP = plt.cm.RdBu_r

    all_vals = np.array([
        *[zones_activity_a.get(z, np.nan) for z in ZONE_NAMES],
        *[zones_activity_b.get(z, np.nan) for z in ZONE_NAMES],
    ])
    grand_mean = np.nanmean(all_vals)
    all_devs = all_vals - grand_mean
    amax = max(abs(np.nanmin(all_devs)), abs(np.nanmax(all_devs)), 1e-9)
    norm = Normalize(vmin=-amax, vmax=amax)

    def _text_color(rgba) -> str:
        r, g, b = rgba[:3]
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return 'black' if luminance > 0.55 else 'white'

    def _draw_grid(ax, activity, title):
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=10, pad=6)

        for i, zone in enumerate(ZONE_NAMES):
            col = i % COLS
            row = i // COLS
            x = col * STEP_X
            y = (ROWS - 1 - row) * STEP_Y

            val = activity.get(zone, grand_mean)
            dev = val - grand_mean
            rgba = CMAP(norm(dev))
            tc = _text_color(rgba)

            rect = mpatches.FancyBboxPatch(
                (x, y), TW, TH,
                boxstyle='round,pad=0.04',
                facecolor=rgba,
                edgecolor='white',
                linewidth=0.8,
            )
            ax.add_patch(rect)

            ax.text(x + TW / 2, y + TH * 0.62, zone,
                    ha='center', va='center',
                    fontsize=11, fontweight='bold', color=tc)
            ax.text(x + TW / 2, y + TH * 0.28, f'{val:.4f}',
                    ha='center', va='center',
                    fontsize=7.5, color=tc, alpha=0.85)
 
        ax.set_xlim(-0.1, COLS * STEP_X - GAP + 0.1)
        ax.set_ylim(-0.25, ROWS * STEP_Y - GAP + 0.25)

    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(7.2, 3.6),
        gridspec_kw={'wspace': 0.10}
    )

    _draw_grid(ax_a, zones_activity_a, label_a)
    _draw_grid(ax_b, zones_activity_b, label_b)

    if title:
        plt.title(title)

    plt.show()


def confusion_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    boundaries: list[float],
    title: str = 'Матрица ошибок модели',
    noimg: bool = False,
    notxt: bool = False,
) -> None:
    """Очень простой визуализатор данных и ошибки на многих классах,
    имеющих чёткое линейное разделение друг от друга по числовой оси"""
    y_cls = np.digitize(y_true, boundaries[1:-1])
    p_cls = np.digitize(y_pred, boundaries[1:-1])

    c_x = [(boundaries[i] + boundaries[i+1]) / 2 for i in range(len(boundaries) - 1)]

    cm = confusion_matrix(y_cls, p_cls, labels=np.arange(len(c_x)))
    labels = [f'{v:.2f}\n({boundaries[i]:.2f}-{boundaries[i+1]:.2f})' for (i, v) in enumerate(c_x)]

    if noimg:
        if not notxt:
            print(f'{title}\n{cm}')

    else:
        cmd = ConfusionMatrixDisplay(cm, display_labels=labels)
        cmd.plot(cmap='Blues', values_format='d')
        plt.title(title)
        plt.show()

    if not notxt:
        print(
            classification_report(
                y_cls,
                p_cls,
                labels=np.arange(len(c_x)),
                target_names=labels,
                zero_division=0
            )
        )
