from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.patheffects as pe


ZONE_NAMES = [
    'LF',
    'MF',
    'RF',
    'LT',
    'MC',
    'RT',
    'LP',
    'MP',
    'RP'
]

ZONE_FULLNAMES = [
    'Left Frontal (LF, № 1)',
    'Midline Frontal (MF, № 2)',
    'Right Frontal (RF, № 3)',
    'Left Temporal (LT, № 4)',
    'Midline Central (MC, № 5)',
    'Right Temporal (RT, № 6)',
    'Left Parietal (LP, № 7)',
    'Midline Parietal (MP, № 8)',
    'Right Parietal (MP, № 9)'
]


def convert_eegc_activity(
    path_input: Path,
    path_out: Path
) -> dict[str, float]:
    df_input = pd.read_csv(path_input)

    df_input['Zone'] = df_input['Zone'].astype(int) # 5.0 --> 5
    zone_means = (
        df_input.groupby('Zone')['Amplitude']
        .mean()
        .reindex(range(1, 10), fill_value=0.0) # 0-8 --> 1-9
    )

    result: dict[str, float] = {
        ZONE_NAMES[zone_id - 1]: float(mean_amp)
        for zone_id, mean_amp in zone_means.items()
    }

    df_out = pd.DataFrame(
        list(result.items()),
        columns=['Zone', 'Amplitude']
    )

    path_out = Path(path_out)
    path_out.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(path_out, index=False)

    return result

def read_zone_activations(
    path_activity: Path
) -> dict[str, float]:
    df = pd.read_csv(path_activity)

    return dict(
        zip(df['Zone'], df['Amplitude'].astype(float))
    )

# Код ниже написан клавдией, чисто для теста данных!

def vis_acitivty_by_zones(
    zones_activity_a: dict[str, float],
    zones_activity_b: dict[str, float],
    label_a: str = 'A',
    label_b: str = 'B',
) -> None:
    """
    Show two side-by-side top-view EEG maps (3x3 zone grids).

    Colour encodes deviation from the grand mean of BOTH maps combined,
    using a single shared scale so the two maps are directly comparable.
    Text colour adapts to tile brightness (dark text on pale tiles).

    Args:
        zones_activity_a: dict mapping zone short-name to mean amplitude (left).
        zones_activity_b: dict mapping zone short-name to mean amplitude (right).
        label_a: title shown above the left map.
        label_b: title shown above the right map.
    """
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
        """Return black or white depending on perceived tile brightness."""
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
            y = (ROWS - 1 - row) * STEP_Y   # row 0 = frontal = top

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

    plt.show()
