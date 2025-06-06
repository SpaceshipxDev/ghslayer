import argparse
import os
from typing import Iterable, Tuple

from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Display.SimpleGui import init_display
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.TDataStd import TDataStd_Name
from OCC.Core.TDF import TDF_LabelSequence


def load_components(path: str) -> Iterable[Tuple[object, str]]:
    """Load a STEP file and return each top-level shape with its name."""
    app = XCAFApp_Application.GetApplication()
    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))
    app.NewDocument("MDTV-XCAF", doc)

    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    status = reader.ReadFile(path)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"Failed to read STEP file: {path}")

    if not reader.Transfer(doc):
        raise RuntimeError("Failed to transfer STEP contents")

    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    labels = TDF_LabelSequence()
    shape_tool.GetFreeShapes(labels)

    components = []
    for i in range(labels.Length()):
        lbl = labels.Value(i + 1)
        shape = shape_tool.GetShape(lbl)
        name_attr = TDataStd_Name()
        name = f"component_{i+1}"
        if lbl.FindAttribute(TDataStd_Name.GetID(), name_attr):
            name = name_attr.Get().ToExtString()
        components.append((shape, name))

    return components


def save_component_images(step_path: str, out_dir: str) -> Iterable[str]:
    """Save each solid from the STEP file as a PNG screenshot.

    Returns an iterable of paths to the saved images."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    components = list(load_components(step_path))

    if not components:
        raise RuntimeError("No solids found in the STEP file")

    display, start_display, add_menu, add_function_to_menu = init_display()
    saved = []
    for i, (solid, name) in enumerate(components, start=1):
        display.EraseAll()
        display.DisplayShape(solid, update=True)
        display.FitAll()
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        if not safe:
            safe = f"component_{i}"
        img_path = os.path.join(out_dir, f"{safe}.png")
        display.View.Dump(img_path)
        saved.append(img_path)
        print(f"Saved {img_path}")

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
