# ChatDocument
## Description

This project is designed to facilitate document upload and interaction via a chat bot, focused on extracting and discussing information from uploaded PDF files.

## Features

- **Document Upload**: Users can upload PDF files containing information for analysis.
- **Chat Bot Interaction**: Utilizes a chat bot to discuss and extract key information from uploaded PDFs.
- **Secure Environment**: Implements environment variables for sensitive data (e.g., API keys, URLs).

## Installation

1. **Clone Repository**
   - Clone the repository:
     git clone https://github.com/your/repository.git
     cd repository

2. **Backend Setup**
   - Navigate to the backend directory:
     cd back_end
   - Install dependencies:
     pip install -r requirements.txt
   - Set environment variables:
     export GEMINI_API_KEY="your_gemini_api_key"
     export REDIS_URL="your_redis_url"
   - Run the backend server:
     uvicorn app:app --reload

3. **Frontend Setup**
   - Navigate to the frontend directory:
     cd front_end
   - Install dependencies:
     npm install
   - Start the frontend server:
     npm start

## Usage

1. **Upload a Document**
   - Access the frontend server (default: http://localhost:3000).
   - Upload a PDF file containing relevant information.

2. **Interact with the Chat Bot**
   - Use the chat interface to discuss and analyze the content of the uploaded PDF.

## Environment Variables

- **GEMINI_API_KEY**: API key for Gemini service.
- **REDIS_URL**: URL for Redis database.

## Contributing

- Phong Pham
- Trung Nguyen
