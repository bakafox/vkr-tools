import argparse
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from window import MainWindow
from yamls import load_zones


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default='./example/images')
    parser.add_argument('-z', type=str, default='./example/rect.yaml')
    parser.add_argument('-o', type=str, default='./example/output')
    args = parser.parse_args()

    img_paths = sorted(
        ip for ip in Path(args.i).iterdir() if ip.is_file()
    )

    zones = load_zones(Path(args.z))

    app = QApplication(sys.argv)

    window = MainWindow(
        zones,
        img_paths,
        Path(args.o),
        [
            # 'hdr', # Heatmap Digits Recognition
            # 'ipp', # Image PreProcessing
            # 'chm', # Colormap Hues Mapping
            # 'zce', # Zone Currents Evaluation
        ]
    )

    window.show()

    sys.exit(app.exec())
