_TODO: write full description here!!1_


## Usage

1. Create new Conda env: `conda env create -f env.yaml`

2. Enter into the created env: `conda activate eegc`

3. Run one of the programs below you need!


## main.py

The main program, used for opening, and playing .SET files as realtime 3D reconstuctions processed through sLORETA. It also allows exporting reconstruction fragments or even individual frames as .CSV files with information for each applied vertex (its zone, coordinates, and amplitude).

Launch: `python3 ./main.py`

*(the program is fully graphical, no arguments needed)*


## preview.py

A simple helper utility to quickly check individual frames exported by EEG-Cutter. Please note that it does NOT allow watching CSVs containing multiple frames. The only _vibecoded_ tool in this project (the entire thing was made by Claude Sonnet 4.6 in just 2 prompts, with many small manual changes afterwards).

Launch: `python3 ./preview.py`

*(the program is fully graphical, no arguments needed)*
