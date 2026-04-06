# InternAI: Multi-Agent Internship Orchestrator

A production-grade, scalable monorepo for automated internship discovery, resume tailoring, and application management.

## 🏗️ Monorepo Architecture

- **`apps/web/`**: Next.js 15+ Frontend (Dashboard, Internship Discovery, AI Drafting).
- **`apps/api/`**: FastAPI (Python) Backend (Multi-agent orchestration, PDF processing, LLM RAG).
- **`packages/`**: Shared configurations and type definitions.

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- **Redis**: Required for scalable session storage. Run via Docker:  `docker run -d -p 6379:6379 redis`
- **Supabase**: Active project with a `resumes` storage bucket created.

### 2. Backend Setup (`apps/api`)
```bash
cd apps/api
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Configure your .env (see .env.example)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup (`apps/web`)
```bash
cd apps/web
npm install
# Ensure .env.local has NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

---

## 🌐 Production Deployment

### Frontend (Vercel)
1. Push this repo to GitHub.
2. Link the repository to **Vercel**.
3. Set the **Root Directory** to `apps/web`.
4. Add the Environment Variable: `NEXT_PUBLIC_BACKEND_URL` (pointing to your live API).

### Backend (Render / Railway / AWS)
1. Use a Python-capable hosting service (e.g., **Render** Web Service).
2. Set the **Root Directory** to `apps/api`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Important**: You must provide a **Redis** instance (e.g., via Render Redis or Upstash).

### 🔐 Environment Variables (Secrets)
- `OPENAI_API_KEY`: Groq/OpenAI key for AI orchestration.
- `SUPABASE_URL` / `SUPABASE_KEY`: Database and Storage connection.
- `REDIS_URL`: Persistent session storage.
- `APIFY_API_KEY`: Live scraper access (optional, falls back to AI simulation).

---

## 🛠️ Features
- **PDF Extraction**: Reliable resume parsing via `pdfplumber`.
- **RAG Engine**: Semantic matching using `sentence-transformers` and `pgvector`.
- **Drafting Workflow**: AI-driven cover letter and tailored resume generation.
- **Fail-safe Logic**: Built-in fallbacks for missing API keys or non-Latin PDF characters.
