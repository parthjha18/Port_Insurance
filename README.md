# Insurance Port Assistant

An AI-powered health insurance portability advisor for India. Upload your existing policy document and get a clear picture of what benefits carry over, what you lose, and whether switching is cost-effective.

## What It Does

- **Extracts** key terms from your porting documents (sum insured, waiting periods, co-pay, NCB, room rent caps, etc.)
- **Compares** your old and new insurer's policy side by side
- **Advises** on cost-effectiveness under IRDAI portability guidelines
- **Answers** natural language questions grounded in your actual policy text

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12) |
| LLM | GPT-4o mini via OpenRouter |
| Vector DB | ChromaDB (local) |
| PDF Parsing | pdfplumber |
| Embeddings | text-embedding-3-small |
| Frontend | React 18 + TailwindCSS + Vite |

## Project Structure

```
Port_Insurance/
├── backend/
│   ├── api/routes/       # FastAPI route handlers
│   ├── core/             # Business logic (parser, embedder, RAG, LLM)
│   ├── models/           # Pydantic schemas
│   ├── main.py           # FastAPI entrypoint
│   └── requirements.txt
├── frontend/             # React + Tailwind UI
├── data/                 # Local PDF storage (gitignored)
├── .env.example          # Environment variable template
└── README.md
```

## Setup

### 1. Clone and configure environment

```bash
git clone https://github.com/parthjha18/Port_Insurance.git
cd Port_Insurance
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a policy PDF, returns `collection_id` |
| `POST` | `/analyze` | Extract structured benefits from uploaded policy |
| `POST` | `/analyze/compare` | Compare two policies side by side |
| `POST` | `/chat` | Ask questions about your policy |
| `GET` | `/personas/demo` | Get demo user personas |
| `GET` | `/health` | Health check |

## Git Workflow

- All development happens on **feature branches** — no direct commits to `main`
- Every branch is merged via a **Pull Request**
- Commits follow **Semantic Commit** format: `type(scope): description`

### Valid commit types

| Type | Use for |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Tooling, config, deps |
| `refactor` | Code restructuring |
| `test` | Tests |

## IRDAI Portability Guidelines

Under IRDAI Health Insurance Regulations:
- Portability request must be submitted **at least 45 days before** policy renewal
- Waiting period credits (pre-existing disease, initial waiting) are **transferable**
- New insurer cannot deny portability without valid grounds
- No-claim bonus may or may not be honoured (insurer-specific)

## Dataset

The `10k_data_li_india.txt` dataset contains LinkedIn profiles of Indian professionals. It is used to generate realistic **demo personas** — e.g., "IT Manager, 35, Bangalore porting from Star Health to HDFC ERGO" — to showcase the assistant's context-aware advice.
