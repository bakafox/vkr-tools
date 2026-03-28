import argparse
import sys
from pathlib import Path
import yaml

from PyQt6.QtWidgets import QApplication

from window import MainWindow


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default='./example/images')
    parser.add_argument('-z', type=str, default='./example/rect.yaml')
    parser.add_argument('-o', type=str, default='./example/output')
    args = parser.parse_args()

    img_paths = sorted(
        ip for ip in Path(args.i).iterdir() if ip.is_file()
    )

    zones = []
    with open(args.z) as f_yaml:
        zones_raw = yaml.safe_load(f_yaml)
        for name, entries in zones_raw.items():
            coords: dict = {}
            if not isinstance(entries, list):
                continue
            for item in entries:
                if isinstance(item, dict):
                    coords.update(item)
            if len(coords) == 4:
                zones.append((name, coords))

    app = QApplication(sys.argv)

    window = MainWindow(
        zones,
        img_paths,
        Path(args.o),
        [
            'hdr', # Heatmap Digits Recognition
            'ipp', # Image PreProcessing
            'che', # Colormap Hues Evaluation
            'cex', # Currents EXtraction
        ]
    )
    window.show()

    sys.exit(app.exec())
