import os
import subprocess
import shutil

# --- Configuration ---
# The name of your PowerPoint file.
# Make sure this file is in the same folder as the script.
PPTX_FILE = "/Users/hashashin/Downloads/01/手板件打样图纸20250514/手板件打样图纸/3D说明.pptx"

# The name of the folder where the slide images will be saved.
OUTPUT_FOLDER = "slide_images"
# ---------------------

def convert_pptx_to_images(pptx_path, output_dir):
    """
    Converts each slide of a PPTX file to a PNG image.
    This function uses a reliable two-step process: PPTX -> PDF -> PNGs.
    """
    # Step 1: Check that all required command-line tools are installed.
    print("Step 1: Checking for required tools...")
    required_tools = ["unoconv", "pdftoppm"]
    for tool in required_tools:
        if not shutil.which(tool):
            print(f"Error: The tool '{tool}' is not installed or not in your PATH.")
            print("Please run the setup commands from the tutorial again.")
            return

    # Step 2: Create the output directory.
    print(f"Step 2: Creating output folder '{output_dir}'...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Step 3: Convert the PPTX to a temporary PDF file.
    # This is often more reliable than converting directly to images.
    print(f"Step 3: Converting '{pptx_path}' to a temporary PDF...")
    temp_pdf_path = os.path.splitext(pptx_path)[0] + '.pdf'

    try:
        # Command to convert PPTX to PDF using unoconv
        pdf_conversion_command = ["unoconv", "-f", "pdf", "-o", temp_pdf_path, pptx_path]
        subprocess.run(pdf_conversion_command, check=True, capture_output=True, text=True)
        print("  -> Successfully created temporary PDF.")

        # Step 4: Convert the PDF into multiple PNG images (one per slide).
        print("Step 4: Converting PDF to PNG images...")
        # This command tells pdftoppm to create PNGs from the PDF.
        image_conversion_command = [
            "pdftoppm",
            "-png",          # Set the output format to PNG
            "-r", "150",     # Set the resolution to 150 DPI (good quality)
            temp_pdf_path,
            os.path.join(output_dir, "slide") # The prefix for the output image names
        ]
        subprocess.run(image_conversion_command, check=True, capture_output=True, text=True)
        print(f"  -> Success! Images are saved in the '{output_dir}' folder.")

    except subprocess.CalledProcessError as e:
        print("\n--- AN ERROR OCCURRED! ---")
        print(f"The command that failed was: {' '.join(e.cmd)}")
        print("Error details:")
        print(e.stderr)
        print("---------------------------\n")
    finally:
        # Step 5: Clean up by deleting the temporary PDF file.
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            print(f"Step 5: Cleaned up temporary file '{temp_pdf_path}'.")

# This is the main part of the script that runs when you execute the file.
if __name__ == "__main__":
    if not os.path.exists(PPTX_FILE):
        print(f"Error: The file '{PPTX_FILE}' was not found in this folder.")
        print("Please make sure your PowerPoint file is in the same directory as this script.")
    else:
        convert_pptx_to_images(PPTX_FILE, OUTPUT_FOLDER)