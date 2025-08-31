import streamlit as st
import json
import base64
import requests
import os
import io
from pdf2image import convert_from_bytes
from PIL import Image

# Title and description for the app
st.set_page_config(page_title="VLM Document Processor", layout="centered")
st.title("📄 VLM Document Processor")
st.markdown("Upload a document (PDF, PNG, JPEG) to categorize it and extract key information using a VLM.")

# Function to call the VLM API
def call_vlm_api(file_data, prompt, mime_type):
    """
    Calls a VLM API to process the file and return a text response.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("API Key not found. Please set the OPENROUTER_API_KEY environment variable.")
        return {"error": "API Key not configured."}

    # Added recommended OpenRouter headers for better practice
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", # Can be your app's URL
        "X-Title": "VLM Document Processor"       # Can be your app's name
    }

    payload = {
        "model": "google/gemini-2.5-flash-image-preview",  # Corrected model ID
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{file_data}"}
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
            content_str = result['choices'][0]['message']['content']
            try:
                # The model can sometimes wrap the JSON in ```json ... ```, so we clean it up
                cleaned_content_str = content_str.strip().replace("```json", "").replace("```", "")
                return json.loads(cleaned_content_str)
            except json.JSONDecodeError:
                st.warning("Failed to parse VLM response as JSON. Displaying raw text:")
                st.text(content_str)
                return {"error": "Failed to parse VLM response as JSON."}
        else:
            return {"error": "No valid response from VLM."}
            
    except requests.exceptions.RequestException as e:
        # Improved error logging to show the actual response from the server
        error_detail = "No additional error detail."
        if e.response is not None:
            try:
                error_detail = e.response.json()
            except json.JSONDecodeError:
                error_detail = e.response.text
        st.error(f"API call failed: {e}")
        st.error(f"Error details: {error_detail}")
        return {"error": "API call failed."}

# File uploader widget
uploaded_files = st.file_uploader(
    "Choose files",
    type=["pdf", "png", "jpeg", "jpg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"Processing: `{uploaded_file.name}`")
        
        bytes_data = uploaded_file.getvalue()
        mime_type = uploaded_file.type

        # --- KEY CHANGE: Handle PDF to Image Conversion ---
        if mime_type == "application/pdf":
            st.info("PDF detected. Converting first page to an image...")
            try:
                # Convert the first page of the PDF to a PIL Image
                images = convert_from_bytes(bytes_data, first_page=1, last_page=1)
                if images:
                    image = images[0]
                    # Convert PIL image to bytes in PNG format
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    bytes_data = buf.getvalue()
                    # Update mime_type for the API call
                    mime_type = "image/png"
                else:
                    st.error("Could not convert PDF to image.")
                    continue
            except Exception as e:
                st.error(f"Failed to process PDF file: {e}")
                continue
        # --- End of Change ---

        # Encode the (potentially converted) file data to base64
        base64_data = base64.b64encode(bytes_data).decode("utf-8")

        prompt = (
            "Analyze this document image, extract key entities, dates, relevant metadata, and return a JSON object with no additional text or markdown formatting. "
            "If the image is an inanimate object like a car, or a lamp, a bicycle, etc. but has no description, then it is likely a marketplace_listing_screenshot. If it has text like model name, price, marketplace website address etc. then it is likely a marketplace_listing_screenshot."
            "The JSON object must contain three keys: 'category', 'extracted_content', and 'description'.\n"
            "1. 'category': Classify the document into one of the following: 'invoice', 'marketplace_listing_screenshot', 'chat_screenshot', 'website_screenshot', or 'other'.\n"
            "2. 'extracted_content': Extract key entities such as names, dates, total amounts, item descriptions, or addresses. Structure this as a dictionary.\n"
            "3. 'description': Write a brief, one-sentence summary of the document's purpose." \
                    )

        with st.spinner("Analyzing document..."):
            processed_data = call_vlm_api(base64_data, prompt, mime_type)

            if isinstance(processed_data, dict) and "error" in processed_data:
                st.error(f"Error processing file: {processed_data['error']}")
            else:
                st.success("Successfully processed!")
                st.json(processed_data)
                
                # --- NEW CODE: Add Download Button ---
                try:
                    json_string = json.dumps(processed_data, indent=2)
                    st.download_button(
                        label="Download JSON Output",
                        data=json_string,
                        file_name=f"{uploaded_file.name}_output.json",
                        mime="application/json",
                    )
                except Exception as e:
                    st.error(f"Failed to create download button: {e}")
                # --- END OF NEW CODE ---
