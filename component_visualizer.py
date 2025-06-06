import argparse
import os
from typing import Iterable, Tuple

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Display.SimpleGui import init_display


def load_step(path: str):
    """Load a STEP file and return the resulting shape."""
    reader = STEPControl_Reader()
    status = reader.ReadFile(path)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"Failed to read STEP file: {path}")
    reader.TransferRoots()
    return reader.OneShape()


def iter_solids(shape):
    """Yield each solid found in the shape."""
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        yield exp.Current()
        exp.Next()


def save_component_images(step_path: str, out_dir: str) -> Iterable[str]:
    """Save each solid from the STEP file as a PNG screenshot.

    Returns an iterable of paths to the saved images."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    shape = load_step(step_path)
    solids = list(iter_solids(shape))

    if not solids:
        raise RuntimeError("No solids found in the STEP file")

    display, start_display, add_menu, add_function_to_menu = init_display()
    saved = []
    for i, solid in enumerate(solids, start=1):
        display.EraseAll()
        display.DisplayShape(solid, update=True)
        display.FitAll()
        img_path = os.path.join(out_dir, f"component_{i}.png")
        display.View.Dump(img_path)
        saved.append(img_path)
        print(f"Saved {img_path}")

    display.Close()
    return saved


def iter_step_files(path: str, recursive: bool = False) -> Iterable[str]:
    """Yield all .stp or .step files from a file or directory path."""
    if os.path.isfile(path):
        return [path]

    step_exts = {".stp", ".step", ".STEP", ".STP"}
    files = []
    if recursive:
        for root, _, filenames in os.walk(path):
            for fname in filenames:
                if os.path.splitext(fname)[1] in step_exts:
                    files.append(os.path.join(root, fname))
    else:
        for fname in os.listdir(path):
            if os.path.splitext(fname)[1] in step_exts:
                files.append(os.path.join(path, fname))
    return files


def process_path(step_path: str, output_dir: str, recursive: bool = False):
    """Process a STEP file or all STEP files in a directory."""
    files = iter_step_files(step_path, recursive=recursive)
    for fpath in files:
        base = os.path.splitext(os.path.basename(fpath))[0]
        out = os.path.join(output_dir, base)
        print(f"Processing {fpath}")
        save_component_images(fpath, out)


def main():
    parser = argparse.ArgumentParser(
        description="Generate screenshots for each component in STEP files",
    )
    parser.add_argument(
        "path",
        help="Path to a STEP/STP file or a directory containing STEP files",
    )
    parser.add_argument(
        "output_dir",
        help="Directory where PNG files will be saved",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for STEP files in subdirectories",
    )
    args = parser.parse_args()

    process_path(args.path, args.output_dir, recursive=args.recursive)


if __name__ == "__main__":
    main()
