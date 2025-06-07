# run_analysis.py
import os
from google import genai
from google.genai import types
from excel_parser import parse_excel_to_gemini_parts

# --- CONFIGURATION ---

# 1. IMPORTANT: Set your Google AI API Key here
#    It's best to set this as an environment variable for security.
#    os.environ['GOOGLE_API_KEY'] = 'YOUR_API_KEY_HERE'
#    For this example, we'll configure it directly. Replace with your key.
try:
    # Replace with your actual API key
    GOOGLE_API_KEY = "AIzaSyCuq4sZ5x_covMuJEuJ6vHbs0I2fKpAQDM"
    
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception:
    print("Error: Could not configure Google AI. Please set your GOOGLE_API_KEY.")
    exit()

# 2. The Excel file you want to analyze
EXCEL_FILE_PATH = "20250528-探野T4-3D打印手板加工清单.xlsx"

# 3. Your prompt/question for the AI
YOUR_PROMPT = """
Analyze the provided Excel data.

Please provide a summary of the 'Products' sheet.
For each product, describe the item based on the data table and the associated image.
"""

# 4. The model to use
MODEL_NAME = "gemini-2.0-flash"

# ---------------------

def main():
    """Main function to run the analysis."""
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"Error: The file '{EXCEL_FILE_PATH}' was not found.")
        return

    # Step 1: Use our parser to get the structured content from Excel
    # This returns a list like [text, text, image_part, text, image_part, ...]
    excel_content_parts = parse_excel_to_gemini_parts(EXCEL_FILE_PATH)
        
    if not excel_content_parts:
        print("Could not parse any content from the Excel file.")
        return

    # Step 2: Combine your prompt with the parsed Excel content
    # The final `contents` list starts with your question.
    final_contents = [YOUR_PROMPT] + excel_content_parts

    print(f"\nSending a prompt with {len(final_contents)} parts to the '{MODEL_NAME}' model...")

    # Step 3: Call the Gemini API
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=final_contents
        )
                
        # Step 4: Print the AI's response
        print("\n--- AI RESPONSE ---")
        print(response.text)
        print("-------------------\n")

    except Exception as e:
        print(f"\nAn error occurred while calling the Gemini API: {e}")

if __name__ == "__main__":
    main()