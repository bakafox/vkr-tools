from pathlib import Path
import pandas as pd


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
    'Left Frontal',
    'Midline Frontal',
    'Right Frontal',
    'Left Temporal',
    'Midline Central',
    'Right Temporal',
    'Left Parietal',
    'Midline Parietal',
    'Right Parietal'
]


def convert_eegc_activity(
    path_input: Path,
    path_out: Path | None = None
) -> dict[str, float]:
    """Перевод кадра с ампл. по вершинам зон в словарь вида { ЗОНА: СР.АМПЛ. }"""

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

    if path_out:
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
    """Чтение уже конвертированных канных, сохранённых функцией выше"""

    return dict(
        zip(df['Zone'], df['Amplitude'].astype(float))
    )
