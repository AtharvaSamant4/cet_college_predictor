import json
from pathlib import Path

from fastapi import APIRouter

from backend.schemas.request_models import CareerQuizRequest
from backend.schemas.response_models import CareerQuizResponse
from career.branch_match_engine import match_branches


ROOT_DIR = Path(__file__).resolve().parents[2]
QUESTION_PATH = ROOT_DIR / "data" / "career_quiz_questions.json"

router = APIRouter(tags=["career-match"])


@router.get("/career-quiz/questions")
def get_career_quiz_questions():
    return {"questions": json.loads(QUESTION_PATH.read_text(encoding="utf-8"))}


@router.post("/career-quiz", response_model=CareerQuizResponse)
def career_quiz(request: CareerQuizRequest):
    return CareerQuizResponse(results=match_branches(request.answers, limit=10))
