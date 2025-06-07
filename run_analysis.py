# run_analysis.py
import os
import google.generativeai as genai
from excel_parser import parse_excel_to_gemini_parts

# --- CONFIGURATION ---

# 1. IMPORTANT: Set your Google AI API Key here
#    It's best to set this as an environment variable for security.
#    os.environ['GOOGLE_API_KEY'] = 'YOUR_API_KEY_HERE'
#    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
#    For this example, we'll configure it directly. Replace with your key.
try:
    # Replace with your actual API key
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE" 
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception:
    print("Error: Could not configure Google AI. Please set your GOOGLE_API_KEY.")
    exit()

# 2. The Excel file you want to analyze
EXCEL_FILE_PATH = "example.xlsx"

# 3. Your prompt/question for the AI
YOUR_PROMPT = """
Analyze the provided Excel data. 
Please provide a summary of the 'Products' sheet. For each product, describe the item based on the data table and the associated image.
"""

# 4. The model to use
MODEL_NAME = "gemini-1.5-flash" # Or "gemini-1.5-pro", etc.

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
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(contents=final_contents)
        
        # Step 4: Print the AI's response
        print("\n--- AI RESPONSE ---")
        print(response.text)
        print("-------------------\n")

    except Exception as e:
        print(f"\nAn error occurred while calling the Gemini API: {e}")


if __name__ == "__main__":
    main()