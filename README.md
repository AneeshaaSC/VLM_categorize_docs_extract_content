# VLM Document Processor


This is a Streamlit application that processes documents (PDFs, PNGs, JPEGs) using a Vision Language Model (VLM) via the OpenRouter API. The application is designed to automatically categorize documents and extract key information from them.

## Features
**Document Upload**: Supports multiple file uploads for PDFs, PNGs, and JPEGs.

**PDF Conversion**: Automatically converts the first page of a PDF file to an image for VLM processing.

**VLM Integration**: Uses the google/gemini-2.5-flash-image-preview model from the OpenRouter API to analyze images.

**Structured Output**: The VLM returns a JSON object containing a category, extracted content, and a brief description of the document.

**Error Handling**: Provides clear messages for API call failures and JSON parsing errors.

## How It Works
The application takes a user-uploaded file, which can be a PDF or an image. If the file is a PDF, it is first converted to an image. The image data is then encoded into a Base64 string and sent to the OpenRouter API, along with a specific prompt. The VLM analyzes the image based on the prompt's instructions and returns a structured JSON response, which is then displayed to the user.

## Setup and Installation

Prerequisites -

1. Python 3.8+
2. A virtual environment (recommended)
3. An API Key from OpenRouter
4. Poppler: For PDF processing, you need to install poppler. On macOS, you can use Homebrew.

Steps

1. Clone the Repository:
```
git clone https://github.com/AneeshaaSC/VLM_categorize_docs_extract_content.git
cd VLM_categorize_docs_extract_content
```

2. Install Poppler (for macOS users):

```
brew install poppler
```

3. Create and Activate a Virtual Environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

4. Install the Required Libraries:
```
pip install streamlit requests pdf2image Pillow
```

5. Set Your API Key:
The application reads the API key from an environment variable. Set it in your terminal before running the app.
```
export OPENROUTER_API_KEY="your_openrouter_api_key_here"
```
(On Windows, use set OPENROUTER_API_KEY="your_openrouter_api_key_here")


6. Run the Streamlit Application:
```
streamlit run app.py
```

The application will open in your browser, and you can begin uploading documents for processing.
