# 🌟 Habitt.site: Smart Habit Tracker & AI Wellness Coach

> A professional full-stack application that combines traditional habit tracking with a RAG-powered (Retrieval-Augmented Generation) AI assistant.

**🔗 [Live Demo: habitt.site](https://habitt.site)**

---

## 🚀 The Core Innovation
Most habit trackers are passive. **Habitt.site** is proactive. 
1. **The Coach (Phase 1):** Analyzes your SQL habit data to find patterns and suggest "Micro-habits."
2. **The Assistant (Phase 2):** A conversational chatbot that uses **RAG** to search through curated wellness guides (Nutrition, Sleep, Exercise) to provide evidence-based advice instead of generic AI guesses.

## 🛠 Technical Stack
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Gunicorn.
- **Frontend:** React.js, Axios, Pico.css, React Router 7.
- **AI Engine:** Google Gemini 2.5 Flash, LangChain, ChromaDB (Vector Store).
- **Infrastructure:** AWS Elastic Beanstalk (API), Google Cloud Storage (Web UI), Cloudflare (SSL/DNS).

## 🏗 System Architecture
This project demonstrates a **Multi-Cloud Distributed System**:
- **AWS (India Region):** Hosts the Dockerized FastAPI engine and SQLite database.
- **GCP:** Hosts the optimized production build of the React frontend.
- **Cloudflare:** Provides a secure SSL bridge between the two clouds, enabling end-to-end HTTPS.

## 📋 Technical Challenges Solved
- **Model Discovery:** Developed a custom diagnostic script to identify and map the correct Gemini 2.5 embedding models (`models/gemini-embedding-001`) during the v1beta API transition.
- **CORS & Security:** Orchestrated Cross-Origin Resource Sharing (CORS) between AWS and GCP to allow secure authenticated requests via JWT.
- **RAG Implementation:** Bypassed standard library bugs by building a custom LangChain wrapper for the Gemini SDK to handle specific task-types for document retrieval.

## ⚙️ How to run locally
1. **Backend:**
   - `cd sql_app`
   - `pip install -r requirements.txt`
   - Create `.env` with `GOOGLE_API_KEY`
   - Run `python ingest.py` to build vector DB.
   - Run `uvicorn main:app --reload`
2. **Frontend:**
   - `cd habit-tracker-frontend`
   - `npm install`
   - `npm start`
