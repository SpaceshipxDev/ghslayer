# Component Visualizer

This repository contains a simple Python script that loads a STEP (`.stp`) file and generates a PNG image for each solid found in the model. The script is intended to demonstrate basic 3D model handling and works on macOS (including Apple silicon) as well as Linux and Windows, assuming the required dependencies are installed.

## Requirements

- Python 3.8+
- [`pythonocc-core`](https://pypi.org/project/pythonocc-core/)
- `PyQt5` or `PyQt6` (required by `pythonocc-core` for visualization)

Install the dependencies with `pip`:

```bash
pip install pythonocc-core PyQt5
```

On Apple silicon Macs you may need to install `pythonocc-core` via [conda](https://docs.conda.io/) or build it from source if the wheel is not available on PyPI.

## Usage

Run the script with the path to a STEP file and the desired output directory:

```bash
python component_visualizer.py path/to/model.stp output_folder
```

Each solid in the STEP file will be rendered to a separate PNG inside `output_folder`.

## Notes

If you run the script on a headless system or wish to suppress the GUI window, set the environment variable `QT_QPA_PLATFORM=offscreen` before running the script:

```bash
QT_QPA_PLATFORM=offscreen python component_visualizer.py model.stp out
```
