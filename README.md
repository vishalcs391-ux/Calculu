# AI Super Study Platform — MVP

An AI-powered study app: upload a PDF or paste a YouTube link → get notes,
flashcards, and a quiz → study, take practice tests, and track progress.

## 1. Product Overview

**Core flow:** Sign in → Upload PDF / paste YouTube link → AI generates notes,
flashcards, quiz → Student studies, takes practice tests, tracks progress.

**8 MVP features:** YouTube→Summary, PDF→Notes, Flashcards, Quiz Generator,
Study Planner, AI Tutor Chat, Exam Practice Tests, Progress Tracker.

**Design principle:** AI is used in small, single-purpose steps (summarize →
flashcards → quiz → tutor reply → practice test) behind a single `AIService`
facade. No router or page ever calls a model provider directly, which is what
makes providers swappable and the AI "not in control of the whole app."

## 2. Folder Structure

```
ai-super-study-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + router wiring
│   │   ├── deps.py                 # get_current_user, require_admin
│   │   ├── core/
│   │   │   ├── config.py           # env-driven settings
│   │   │   ├── database.py         # SQLAlchemy engine/session
│   │   │   └── security.py         # Firebase token verification
│   │   ├── models/                 # SQLAlchemy ORM models (1 per table)
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── routers/                # auth, sources, content, study,
│   │   │                           # progress, billing, admin
│   │   └── services/
│   │       ├── ai/                 # provider abstraction (ollama/hf/openai)
│   │       ├── pdf_service.py
│   │       ├── youtube_service.py
│   │       ├── flashcard_service.py
│   │       ├── quiz_service.py
│   │       ├── study_planner_service.py
│   │       └── progress_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html          # sign in / sign up
│   ├── dashboard.html      # progress + upcoming sessions
│   ├── upload.html         # PDF upload + YouTube link
│   ├── flashcards.html
│   ├── quiz.html
│   ├── planner.html
│   ├── tutor.html
│   ├── progress.html
│   ├── css/styles.css
│   └── js/                 # firebase-config, api, auth, per-page scripts
└── database/
    └── schema.sql
```

This maps 1:1 to the "modular backend" requirement: **auth** (auth router +
security.py), **source processing** (sources router + pdf/youtube services),
**content generation** (content router + AI service), **study tools** (study
router + planner service), **progress tracking** (progress router), **billing**
(billing router), **admin analytics** (admin router).

## 3. Database

See `database/schema.sql` for the full DDL (also mirrored as SQLAlchemy
models in `backend/app/models/`). Tables: `users`, `sources`, `summaries`,
`flashcards`, `quizzes`, `practice_tests`, `study_sessions`,
`progress_metrics`, `subscriptions`. All use UUID primary keys, FK cascades,
`created_at`/`updated_at` timestamps, and indexes on foreign keys and
frequently-filtered columns (`status`, `next_review_at`, `metric_date`).

## 4. API Routes (prefix `/api/v1`)

| Module | Route | Method | Purpose |
|---|---|---|---|
| auth | `/auth/me` | GET | Current user profile (auto-provisioned from Firebase) |
| sources | `/sources/pdf` | POST | Upload PDF, extract text |
| sources | `/sources/youtube` | POST | Add YouTube link, fetch transcript |
| sources | `/sources` | GET | List my sources |
| content | `/content/sources/{id}/summarize` | POST | AI: raw text → notes |
| content | `/content/summaries/{id}/flashcards` | POST/GET | AI: generate / list flashcards |
| content | `/content/flashcards/{id}/review` | POST | Record review (spaced repetition) |
| content | `/content/summaries/{id}/quiz` | POST | AI: generate quiz |
| content | `/content/quizzes/{id}/submit` | POST | Score quiz |
| study | `/study/planner` | POST/GET | Create / list study plan |
| study | `/study/planner/{id}/complete` | PATCH | Mark session done |
| study | `/study/tutor/chat` | POST | AI tutor reply |
| study | `/study/practice-tests` | POST/GET | AI: generate practice test |
| study | `/study/practice-tests/{id}/submit` | POST | Score practice test |
| progress | `/progress` | GET | Dashboard rollup (streak, minutes, scores) |
| billing | `/billing/plans` | GET | Plan catalog |
| billing | `/billing/checkout` | POST | Stripe checkout (placeholder) |
| billing | `/billing/webhook` | POST | Stripe webhook (placeholder) |
| admin | `/admin/stats` | GET | Usage stats (admin-only) |

Interactive docs are auto-generated at `/docs` once the backend is running.

## 5. Frontend Pages

`index.html` (auth) · `dashboard.html` · `upload.html` · `flashcards.html` ·
`quiz.html` · `planner.html` · `tutor.html` · `progress.html`

Vanilla HTML/CSS/JS with ES modules, one script per page, plus a shared
`api.js` (attaches Firebase ID token to every request) and `auth.js`.

## 6. AI Provider Abstraction

`backend/app/services/ai/base.py` defines `AIProvider.generate()`.
`ollama_provider.py`, `huggingface_provider.py`, `openai_provider.py` each
implement it. `ai_service.py` is the only thing routers/services call, and it
picks a provider based on `AI_PROVIDER` in `.env`. To add a new provider
(e.g. Anthropic), implement `AIProvider` and add one branch in
`AIService._select_provider()` — nothing else changes.

## 7. Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node not required (frontend is static)
- [Ollama](https://ollama.com) installed locally (or a Hugging Face / OpenAI API key)
- A Firebase project with Email/Password auth enabled

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: DATABASE_URL, FIREBASE_SERVICE_ACCOUNT_JSON, AI_PROVIDER, etc.

# Create the database once:
createdb study_platform
psql study_platform < ../database/schema.sql

# Pull a local model if using Ollama (default):
ollama pull llama3.1
ollama serve

uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to confirm the API is up.

### Frontend

1. In `frontend/js/firebase-config.js`, paste your Firebase web app config
   (Firebase Console → Project Settings → General → Your apps).
2. In `frontend/js/api.js`, confirm `API_BASE` points at your backend
   (`http://localhost:8000/api/v1` locally).
3. Serve the folder with any static server, e.g.:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
4. Open `http://localhost:5500`.

### Firebase Admin credentials (backend)

Download a service account JSON from Firebase Console → Project Settings →
Service Accounts → Generate new private key. Save it as
`backend/firebase-service-account.json` and point
`FIREBASE_SERVICE_ACCOUNT_JSON` at it in `.env`.

## 8. Deployment

**Frontend → GitHub Pages**
1. Push the `frontend/` folder to a GitHub repo (or a `docs/` subfolder).
2. In repo Settings → Pages, set the source to that folder/branch.
3. Update `API_BASE` in `api.js` to your deployed backend URL before pushing.

**Backend → Render or Railway**
1. Push `backend/` to GitHub.
2. Create a new Web Service, root directory `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add a managed PostgreSQL instance (Render/Railway both offer one-click
   Postgres) and set `DATABASE_URL` to its connection string.
6. Run `database/schema.sql` against the managed DB once (via `psql` or the
   provider's SQL console).
7. Set all `.env` variables in the host's environment variable settings,
   including `FIREBASE_SERVICE_ACCOUNT_JSON` (as inline JSON or a secret
   file, depending on host) and `AI_PROVIDER` (use `openai` or
   `huggingface` in production unless you're self-hosting Ollama on a GPU
   box — Ollama's localhost default won't be reachable from a hosted
   backend).
8. Update `FRONTEND_ORIGIN` to your GitHub Pages URL for CORS.

## 9. Monetization (design, wired for v2)

Plan catalog lives in `billing.py` / `PLAN_CATALOG` and mirrors the
`subscriptions` table: `free`, `premium_monthly`, `student_yearly`,
`school` (seat-based), `teacher`. Checkout/webhook endpoints are stubbed —
plug in real Stripe keys and the existing shape stays the same.

## 10. Phased Roadmap

**v1 (this MVP)** — the 8 features above, synchronous processing, email/password auth.

**v1.1**
- Background job queue (Celery/RQ + Redis) for PDF/YouTube processing so
  large files don't block the request.
- Google Sign-In via Firebase.
- Real Stripe checkout + webhook handling.

**v2**
- Smarter spaced repetition (full SM-2 algorithm) for flashcards.
- AI-prioritized study planner (weak-topic detection from quiz history).
- Multi-source practice tests spanning a whole course, not just one upload.
- Mobile-responsive polish pass / PWA install support.

**v3**
- Teacher/classroom accounts: assign material, see class-wide progress.
- School/college license management (bulk seats, admin console).
- React migration for the frontend as feature surface grows.
- Usage-based rate limiting enforced server-side per plan tier.

**v4**
- Collaborative study groups / shared flashcard decks.
- Native mobile app (Claude Code / React Native) wrapping the same API.
- Advanced admin analytics dashboard (retention, feature usage, billing health).

## Note on the 1-week build & rate limits

This scaffold is meant to be built incrementally, in this order, so it stays
demoable at every step even if you hit usage limits or need to pause:
1. DB schema + auth (`users` table, `/auth/me`) — day 1
2. PDF/YouTube ingestion (`sources`) — day 2
3. AI summarize → notes (`summaries`) — day 2-3
4. Flashcards + quiz generation — day 3-4
5. Study planner + progress tracker — day 5
6. AI tutor chat + practice tests — day 6
7. Billing plan catalog + admin stats + polish — day 7

Each step above is already a working vertical slice in this codebase, so you
can stop after any one of them and still have something that runs.
