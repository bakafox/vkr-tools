import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
from typing import Literal

from importer import ZONE_FULLNAMES, ZONE_NAMES


def confusion_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    boundaries: list[float],
    title: str = 'Матрица ошибок модели',
    noimg: bool = False,
    notxt: bool = False,
) -> dict:
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
    
    return classification_report(
        y_cls,
        p_cls,
        output_dict=True,
        labels=np.arange(len(c_x)),
        target_names=labels,
        zero_division=0
    )


def vis_importances_map(
    importances: list[np.float32],
    input_names: list[str],
    group_names: list[str],
    mode: Literal['spatial', 'spectral'],
    suptitle: str = 'Карта важности признаков',
    cmap_limits: tuple[float, float] | None = (-0.001, 0.001)
) -> None:
    """Визуализатор feature importance для результатов модели для
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
) -> None:
    """Визуализатор данных в виде розы ветров (на самом деле
    это просто секторальная диаграмма, потому что роза ветров
    на моих данных выглядела просто максимально нечитабельно,
    но научрук просила именно розу ветров, так что...)"""
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
