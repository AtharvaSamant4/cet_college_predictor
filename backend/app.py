from pathlib import Path
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.routes import career, forecast, metadata, recommend, student_tools


def parse_allowed_origins():
    raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


allowed_origins = parse_allowed_origins()


app = FastAPI(
    title="Maharashtra CET College Predictor API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router)
app.include_router(career.router)
app.include_router(forecast.router)
app.include_router(metadata.router)
app.include_router(student_tools.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
