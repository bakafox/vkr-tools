import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
from matplotlib.cm import ScalarMappable
from typing import Literal

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


def vis_importances_map(
    importances: list[np.float32],
    input_names: list[str],
    group_names: list[str],
    mode: Literal['spatial', 'spectral'],
    suptitle: str = 'Карта важности признаков',
    cmap_limits: tuple[float, float] | None = (-0.001, 0.001)
) -> None:
    """Виузализатор feature importance для результатов модели для
    простр. (mode='spacial') и спектр. (mode='spectral') хар-к"""
    cmap = plt.cm.PiYG

    if cmap_limits is not None:
        norm = Normalize(vmin=cmap_limits[0], vmax=cmap_limits[1])
    else:
        norm = Normalize(vmin=min(importances), vmax=max(importances))

    fig = plt.figure()
    fig.suptitle(suptitle)

    feat_dict = dict(zip(input_names, importances))
    grid_left = 0.04
    grid_top = 0.88

    if mode == 'spatial':
        labels = ['Начачо\nпредъяв.', 'Конец\nпредъяв.']
    else:
        labels = ['δ', 'θ', 'α', 'β', 'γ']

    for i, (row, col) in enumerate([
        (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)
    ]):
        x = grid_left + col * 0.28
        y = grid_top - row * 0.27

        ax = fig.add_axes([x, y - 0.2, 0.25, 0.2])
        ax.set_xlim(0, len(labels))
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(ZONE_FULLNAMES[i])

        for rect_idx in range(len(labels)):
            if mode == 'spatial':
                key = f'{ZONE_NAMES[i]}_{rect_idx + 1}'
            else:
                key = f'{labels[rect_idx]}_{ZONE_NAMES[i]}'

            val = feat_dict.get(key, 0.0)
            color = cmap(norm(val))
            rect = mpatches.FancyBboxPatch(
                (rect_idx + 0.3, 0.06), 0.9, 0.9,
                facecolor=color, linewidth=0
            )
            ax.add_patch(rect)
            ax.text(
                rect_idx + 0.5, 0.48, labels[rect_idx],
                ha='center', va='center', fontsize=8, color='black'
            )

    meta_y = grid_top - 3 * (0.2 + 0.04) - 0.06
    meta_features = ['gender', *group_names]

    ax_meta = fig.add_axes([grid_left, meta_y - 0.07, 0.81, 0.07])
    ax_meta.set_xlim(0, len(meta_features))
    ax_meta.set_ylim(0, 1)
    ax_meta.set_xticks([])
    ax_meta.set_yticks([])

    for i, feat in enumerate(meta_features):
        val = feat_dict.get(feat, 0.0)
        color = cmap(norm(val))
        rect = mpatches.FancyBboxPatch(
            (i + 0.3, 0.06), 0.9, 0.9,
            facecolor=color, linewidth=0
        )
        ax_meta.add_patch(rect)
        ax_meta.text(
            i + 0.5, 0.48, feat[:6],
            ha='center', va='center', fontsize=8, color='black'
        )

    cbar_ax = fig.add_axes([0.9, 0.16, 0.02, 0.7])
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, cax=cbar_ax, label='Оценка важности признака')
    plt.show()


def vis_circular_accuracy(
    errors_a: list[float],
    errors_b: list[float],
    labels: list[str],
    titles: list[str],
    suptitle: str | None = None,
    lpos: tuple[float, float] = (1.00, 1.00),
    text: str = ''
):
    """Визуализатор данных в виде розы ветров (на самом деле
    не совсем, потому что секторальная диаграмма всё же более
    удобочитаема, но научрук просила именно розу ветров)"""
    assert(len(errors_a) == len(errors_b) == len(labels))

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)

    ax.bar(angles, errors_b, width=2*np.pi / len(labels), label=titles[0], color='lightgreen')
    ax.bar(angles, errors_a, width=2*np.pi / len(labels), label=titles[1], color='green')

    ax.set_xticks(angles)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper right', bbox_to_anchor=lpos)
    if suptitle:
        plt.title(suptitle)
    ax.text(0, 1, text, transform=ax.transAxes, fontsize=12)

    plt.show()
