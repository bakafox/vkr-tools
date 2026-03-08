from pathlib import Path


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


def load_zones(filepath: str) -> dict[str, list[str]]:
    zones = {}

    for line in Path(filepath).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        zone_name, _, channels_str = line.partition(':')
        zone_name = zone_name.strip()
        if zone_name not in ZONE_NAMES:
            continue
        zones[zone_name] = channels_str.split()

    return zones


def create_reverse_map(zone_labels: dict[str, list[str]]) -> dict[str, int]:
    reverse_zones = {}

    for zone_name, channels in zone_labels.items():
        zone_idx = ZONE_NAMES.index(zone_name) + 1
        for ch in channels:
            reverse_zones[ch.lower()] = zone_idx

    return reverse_zones


def get_zone_name(zone_idx: int) -> str:
    try:
        return ZONE_FULLNAMES[zone_idx - 1]
    except Exception:
        return '(unassigned)'
