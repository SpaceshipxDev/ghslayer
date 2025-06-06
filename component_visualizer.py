import argparse
import os
from typing import Iterable

# I've kept all your imports, they are correct.
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

# CHANGE 1: The function now accepts the 'display' object as an argument.
# It no longer creates or closes the display itself.
def save_component_images(step_path: str, out_dir: str, display) -> Iterable[str]:
    """Save each solid from the STEP file as a PNG screenshot.

    Returns an iterable of paths to the saved images."""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    shape = load_step(step_path)
    solids = list(iter_solids(shape))

    if not solids:
        print(f"Warning: No solids found in the STEP file {step_path}. Skipping.")
        return []

    saved = []
    for i, solid in enumerate(solids, start=1):
        display.EraseAll()
        display.DisplayShape(solid, update=True)
        display.FitAll()
        img_path = os.path.join(out_dir, f"component_{i}.png")
        display.View.Dump(img_path)
        saved.append(img_path)
        print(f"Saved {img_path}")
        
    # CHANGE 2: Removed the 'display.Close()' line which was causing the crash.
    # The display is now managed by the calling function.
    return saved


def iter_step_files(path: str, recursive: bool = False) -> Iterable[str]:
    """Yield all .stp or .step files from a file or directory path."""
    if os.path.isfile(path):
        # If it's a file, just yield that one file if it's a step file
        if os.path.splitext(path)[1].lower() in {".stp", ".step"}:
            yield path
        return

    step_exts = {".stp", ".step"}
    
    if recursive:
        for root, _, filenames in os.walk(path):
            for fname in filenames:
                if os.path.splitext(fname)[1].lower() in step_exts:
                    yield os.path.join(root, fname)
    else:
        for fname in os.listdir(path):
            full_path = os.path.join(path, fname)
            if os.path.isfile(full_path) and os.path.splitext(fname)[1].lower() in step_exts:
                yield full_path


def process_path(input_path: str, output_dir: str, recursive: bool = False):
    """Process a STEP file or all STEP files in a directory."""
    
    # CHANGE 3: Initialize the display ONCE, before processing any files.
    # We only need the 'display' object from the tuple it returns.
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # Get all the file paths first
    files_to_process = list(iter_step_files(input_path, recursive=recursive))

    if not files_to_process:
        print(f"No STEP/STP files found in '{input_path}'.")
        return

    for fpath in files_to_process:
        # Create a unique sub-directory for each STEP file's components
        base = os.path.splitext(os.path.basename(fpath))[0]
        out_subdir = os.path.join(output_dir, base)
        
        print(f"\nProcessing {fpath}...")
        try:
            # CHANGE 4: Pass the single, shared 'display' object to the function.
            save_component_images(fpath, out_subdir, display)
        except Exception as e:
            print(f"!!!!!!!! FAILED to process {fpath}: {e} !!!!!!!!")


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
    print("\nAll done.")


if __name__ == "__main__":
    main()