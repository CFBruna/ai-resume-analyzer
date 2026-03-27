# AI Resume Analyzer

AI-powered resume analysis platform for recruitment teams. Upload PDF or image resumes and receive structured summaries or ask recruitment questions answered with evidence-based justifications.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

First startup note: LocalAI downloads `phi-4-mini` on first run, so startup can take a few minutes.

## Endpoints

- `GET /health`
- `POST /api/v1/resumes/analyze`

## API Usage

### Summaries

```bash
curl -X POST http://localhost:8000/api/v1/resumes/analyze \
  -F "files=@resume.pdf" \
  -F "request_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "user_id=recruiter@company.com"
```

### Query

```bash
curl -X POST http://localhost:8000/api/v1/resumes/analyze \
  -F "files=@resume_a.pdf" \
  -F "files=@resume_b.pdf" \
  -F "request_id=550e8400-e29b-41d4-a716-446655440001" \
  -F "user_id=recruiter@company.com" \
  -F "query=Which candidate has more Python and cloud experience?"
```

## LLM Provider

The adapter is provider-agnostic. To switch from LocalAI to OpenAI-compatible endpoints, update only these env vars:

```env
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini
```

## Architecture

- `domain/` entities and ports
- `application/` use cases
- `infrastructure/` OCR, LLM and persistence adapters
- `presentation/` FastAPI routes, schemas and DI

## Local URLs

- Swagger: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health
