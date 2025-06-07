from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCuq4sZ5x_covMuJEuJ6vHbs0I2fKpAQDM")

# Upload the first image
image1_path = "input/Screenshot 2025-06-07 at 8.30.17 PM.png"
uploaded_file = client.files.upload(file=image1_path)

# Prepare the second image as inline data
image2_path = "input/Screenshot 2025-06-07 at 8.30.17 PM.png"
with open(image2_path, 'rb') as f:
    img2_bytes = f.read()

# Create the prompt with text and multiple images
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        "What is different between these two images?",
        uploaded_file,  # Use the uploaded file reference
        types.Part.from_bytes(
            data=img2_bytes,
            mime_type='image/png'
        )
    ]
)

print(response.text)