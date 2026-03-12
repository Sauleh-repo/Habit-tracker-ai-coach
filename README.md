# Habitt.site: Smart Habit Management & RAG-Powered AI Coaching

A full-stack behavioral tracking platform that utilizes Retrieval-Augmented Generation (RAG) and proactive LLM analysis to provide data-grounded wellness coaching.

**[Live Demo](https://habitt.site)** | **[Backend API Docs](https://api.habitt.site/docs)**

---

## Project Overview
Habitt.site is a distributed system designed to move beyond passive habit tracking. By integrating the Google Gemini 2.5 Flash model with a custom vector database, the application provides two distinct AI interventions:
1.  **Proactive Behavioral Analysis:** Periodically analyzes SQL-resident habit data to identify patterns and suggest actionable "micro-habits."
2.  **Context-Aware Assistant (RAG):** A conversational interface that performs semantic searches over curated wellness datasets (Nutrition, Sleep, Exercise) to ensure advice is grounded in expert knowledge rather than model hallucinations.

## Technical Stack

### Backend & AI Infrastructure
*   **Language/Framework:** Python 3.11, FastAPI (Asynchronous)
*   **Database (RDBMS):** SQLAlchemy ORM with SQLite
*   **Vector Store:** ChromaDB
*   **Orchestration:** LangChain
*   **LLM:** Google Gemini 2.5 Flash (Generative) & Gemini-Embedding-001 (Embeddings)

### Frontend
*   **Framework:** React.js (Single Page Application)
*   **State Management:** React Hooks & Context API
*   **Styling:** Pico.css (Semantic HTML framework)
*   **Routing:** React Router 7 (Hash-based for cloud compatibility)

### DevOps & Cloud Architecture
*   **Backend Hosting:** AWS Elastic Beanstalk (Linux/Docker)
*   **Frontend Hosting:** Google Cloud Storage (Static Website Bucket)
*   **Security/DNS:** Cloudflare (SSL/TLS Termination & Edge Proxy)
*   **Containerization:** Docker

## System Architecture
This project implements a **Multi-Cloud Distributed Architecture**:
*   **API Layer:** Hosted on AWS (ap-south-1) to leverage Elastic Beanstalk's auto-scaling and robust environment management.
*   **Static Asset Layer:** Hosted on GCP for low-latency delivery of the React production build.
*   **Security Bridge:** Cloudflare acts as the global proxy, enforcing HTTPS/SSL across both cloud providers and resolving Cross-Origin Resource Sharing (CORS) requirements between the `api.habitt.site` and `habitt.site` origins.

## Engineering Challenges & Solutions

### 1. RAG SDK Compatibility
*   **Issue:** Standard LangChain wrappers for Google Generative AI encountered 404 errors due to the rapid transition of the Gemini v1beta API.
*   **Solution:** Engineered a custom Embedding Wrapper class to interface directly with the `google-genai` SDK, implementing explicit `task_type` definitions (`retrieval_document` vs `retrieval_query`) to ensure vector consistency.

### 2. Multi-Cloud CORS Management
*   **Issue:** Browsers blocked authenticated requests between the GCP-hosted frontend and AWS-hosted backend.
*   **Solution:** Configured FastAPI middleware with a specific allow-list of production origins and implemented JWT (JSON Web Token) based authentication to secure PII (Personally Identifiable Information) across domains.

### 3. Client-Side Routing in Static Storage
*   **Issue:** Standard browser routing caused 404 errors on GCP buckets when refreshing sub-pages.
*   **Solution:** Implemented `HashRouter` to manage application state via the URL fragment, ensuring the application remains a seamless SPA (Single Page Application) in a static hosting environment.

## Local Development Setup

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Google Gemini API Key

### Backend Setup
1. `cd sql_app`
2. `pip install -r requirements.txt`
3. Configure `.env` file with `GOOGLE_API_KEY`
4. Execute `python ingest.py` to initialize the ChromaDB vector store.
5. Launch server: `uvicorn main:app --reload`

### Frontend Setup
1. `cd habit-tracker-frontend`
2. `npm install`
3. Configure `baseURL` in `src/services/api.js` to `http://localhost:8000`
4. Launch application: `npm start`

---
*Developed as a proof-of-concept for RAG-integrated full-stack architectures.*
