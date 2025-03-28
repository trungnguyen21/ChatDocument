# ChatDocument

This is a simple Retrieval Augmented Generation app (RAG) with a full-fledged user interface!

## 📄 Features (new updates!)

- **Document Upload**: Users can upload PDF files up to 3145728B (~3MB) containing information for analysis.
- **Google Gemini Pro**: Leveraging Google's latest LLM with 2 million token contexts to craft responses and embeddings.
- **State-of-the-art UI**: Can't go wrong with React + Bootstrap
- **HTTPS**: Deployed on a VPS with a valid SSL certificate
- (new) **Celery task queue**: paired with Redis to improve application responsiveness + enhanced scalability

## 🔧 Tech stack
- Server: Langchain, FastAPI, Redis, Celery
- Client: React, Bootstrap

## 📦 Installation
1. Clone the repository
2. Make sure you are on the branch `main`
3. cd into `main`
4. Add GOOGLE_API_KEY and REDIS_URL as variables in the `app/.env`
  - Google Gemini: https://ai.google.dev/gemini-api
  - Redis: https://redis.io/
5. `docker compose up` 

## 🔄 System structure (feedback appreciated!)
<img width="590" alt="image" src="https://github.com/user-attachments/assets/ea5b213f-5942-4633-bc36-f1e7b87ca71f">

## 📋 TODOs:
- [x] Create the app itself :D
   - [x] PDF reader
   - [x] RAG chain with context and chat history
   - [x] REST api endpoints
   - [x] React app client
- [ ] ~~Deploy on Vercel~~ File too large
- [x] Deploy on a VPS with `nginx` and `pm2`

## 👥 Contributors
- Phong Pham
- Trung Nguyen
