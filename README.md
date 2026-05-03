# SkillLens

SkillLens is a production-grade hackathon MVP that compares claimed resume skills against real GitHub evidence, optional LeetCode data, and a multi-source RAG mentor system.

## Stack

- Frontend: React 19, TypeScript, Vite, Tailwind CSS, Framer Motion
- Backend: FastAPI, Groq `llama-3.3-70b-versatile`, GitHub REST, FAISS, sentence-transformers

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set `GROQ_API_KEY` for resume parsing, roadmap generation, and mentor chat. Set `GITHUB_TOKEN` to improve GitHub API rate limits.

## Run Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Test

```bash
cd backend
pytest

cd ../frontend
npm run build
```

## Deployment

- Frontend: deploy `/frontend` to Vercel with `VITE_API_BASE_URL` pointing to the backend.
- Backend: deploy `/backend` to Render or Railway using:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure production CORS with `FRONTEND_ORIGIN=https://your-vercel-domain`.
