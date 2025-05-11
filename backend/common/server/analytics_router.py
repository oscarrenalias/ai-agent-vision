import os

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from common.analytics import calculate_daily_spend, calculate_monthly_spend, calculate_yearly_spend

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DATABASE", "receipts")
AGGREGATES_COLLECTION = "aggregates"

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]

analytics_router = APIRouter()


@analytics_router.get("/analytics/monthly_spend")
async def get_monthly_spend(year: int = Query(None), month: int = Query(None)):
    """
    Returns monthly spend aggregates (overall, level_1, level_2) for all months or filtered by year/month if provided.
    """
    doc = await db[AGGREGATES_COLLECTION].find_one({"type": "monthly_spend"})
    if not doc or "data" not in doc:
        return JSONResponse(content={"error": "No monthly spend data found."}, status_code=404)
    data = doc["data"]

    # Optionally filter by year/month
    def filter_month(arr):
        result = arr
        if year is not None:
            result = [d for d in result if d["_id"].get("year") == year]
        if month is not None:
            result = [d for d in result if d["_id"].get("month") == month]
        return result

    data = {
        "overall": filter_month(data.get("overall", [])),
        "level_1": filter_month(data.get("level_1", [])),
        "level_2": filter_month(data.get("level_2", [])),
    }
    return {"monthly_spend": data}


@analytics_router.get("/analytics/yearly_spend")
async def get_yearly_spend(year: int = Query(None)):
    """
    Returns yearly spend aggregates (overall, level_1, level_2, level_3) for all years or a specific year if provided.
    """
    doc = await db[AGGREGATES_COLLECTION].find_one({"type": "yearly_spend"})
    if not doc or "data" not in doc:
        return JSONResponse(content={"error": "No yearly spend data found."}, status_code=404)
    data = doc["data"]
    # Optionally filter by year
    if year is not None:

        def filter_year(arr, key="year"):
            return [d for d in arr if d["_id"].get(key) == year]

        data = {
            "overall": filter_year(data.get("overall", [])),
            "level_1": filter_year(data.get("level_1", [])),
            "level_2": filter_year(data.get("level_2", [])),
            "level_3": filter_year(data.get("level_3", [])),
        }
    return {"yearly_spend": data}


@analytics_router.get("/analytics/yearly_spend_full")
async def get_yearly_spend_full(year: int = Query(None)):
    """
    Returns yearly spend aggregates (overall, level_1, level_2, level_3) for all years or a specific year if provided.
    """
    doc = await db[AGGREGATES_COLLECTION].find_one({"type": "yearly_spend"})
    if not doc or "data" not in doc:
        return JSONResponse(content={"error": "No yearly spend data found."}, status_code=404)
    data = doc["data"]
    # Optionally filter by year
    if year is not None:

        def filter_year(arr, key="year"):
            return [d for d in arr if d["_id"].get(key) == year]

        data = {
            "overall": filter_year(data.get("overall", [])),
            "level_1": filter_year(data.get("level_1", [])),
            "level_2": filter_year(data.get("level_2", [])),
            "level_3": filter_year(data.get("level_3", [])),
        }
    return {"yearly_spend": data}


@analytics_router.get("/analytics/recalculate")
async def recalculate_aggregates():
    """
    Manually trigger recalculation of all analytics aggregates (yearly, monthly, daily).
    """
    await calculate_yearly_spend()
    await calculate_monthly_spend()
    await calculate_daily_spend()
    return {"status": "ok", "message": "Recalculated yearly, monthly, and daily spend aggregates."}
