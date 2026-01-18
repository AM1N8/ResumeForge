# AI Resume Structuring Agent

An intelligent agent that takes unstructured resumes (PDF, Markdown, LaTeX) and GitHub profiles to create a polished, canonical resume structure optimized for internship applications.

## Project Structure

- **/backend**: FastAPI application, SQLAlchemy models, Groq LLM integration.
- **/frontend**: React + Vite + Tailwind CSS + Shadcn/UI dashboard.
- **/scripts**: Verification and utility scripts.

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/)
- [GitHub Personal Access Token](https://github.com/settings/tokens) (Optional, for higher rate limits)

## Installation

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Update .env with your GROQ_API_KEY and GITHUB_TOKEN
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## How to Run

### Start the Backend

```bash
cd backend
# Make sure venv is active
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.

### Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Verification

You can run the backend verification script to ensure your environment is set up correctly:

```bash
python scripts/verify_backend.py
```
