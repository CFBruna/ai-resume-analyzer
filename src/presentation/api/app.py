from fastapi import FastAPI

app = FastAPI(
    title="AI Resume Analyzer",
    description="AI-powered resume analysis platform for recruitment teams",
    version="1.0.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
