from pathlib import Path

import yaml


def load_zones(
    yaml_path: Path
) -> list[tuple[str, dict]]:
    zones = []

    with open(yaml_path) as yaml_f:
        zones_raw = yaml.safe_load(yaml_f)
        for name, entries in zones_raw.items():
            coords: dict = {}
            if not isinstance(entries, list):
                continue
            for item in entries:
                if isinstance(item, dict):
                    coords.update(item)
            if len(coords) == 4:
                zones.append((name, coords))
    
    return zones


def save_results(
    results: list[tuple[str, list[dict[str, str | float | int]]]],
    out_dir: Path
):
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename, filedata in results:
        output_data = {
            fdd['zone']: fdd['amplitude'] 
            for fdd in filedata
        }
        
        yaml_path = out_dir / f'{filename}.yaml'
        with open(yaml_path, 'w', encoding='utf-8') as yaml_f:
            yaml.safe_dump(output_data, yaml_f, sort_keys=False)
