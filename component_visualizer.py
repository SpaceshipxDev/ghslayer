import argparse
import os
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


def save_component_images(step_path: str, out_dir: str):
    """Save each solid from the STEP file as a PNG screenshot."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    shape = load_step(step_path)
    solids = list(iter_solids(shape))

    if not solids:
        raise RuntimeError("No solids found in the STEP file")

    display, start_display, add_menu, add_function_to_menu = init_display()

    for i, solid in enumerate(solids, start=1):
        display.EraseAll()
        display.DisplayShape(solid, update=True)
        display.FitAll()
        img_path = os.path.join(out_dir, f"component_{i}.png")
        display.View.Dump(img_path)
        print(f"Saved {img_path}")

    display.Close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate screenshots for each component in a STEP file"
    )
    parser.add_argument("step_file", help="Path to the STEP/STP file")
    parser.add_argument("output_dir", help="Directory where PNG files will be saved")
    args = parser.parse_args()

    save_component_images(args.step_file, args.output_dir)


if __name__ == "__main__":
    main()
