from fastapi import APIRouter

router = APIRouter(tags=["forecast"])

@router.get("/forecast")
def get_forecast():
    return {"message": "Forecasts are now directly computed from DB."}
