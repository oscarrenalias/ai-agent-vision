import os

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from common.analytics import (
    calculate_daily_spend,
    calculate_monthly_spend,
    calculate_weekly_spend,
    calculate_yearly_monthly_spend,
    calculate_yearly_spend,
)

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DATABASE", "receipts")
AGGREGATES_COLLECTION = "aggregates"

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]

analytics_router = APIRouter()


@analytics_router.get("/analytics/monthly_spend")
async def get_monthly_spend(year: int = Query(None), month: int = Query(None)):
    """
    Returns monthly spend aggregates (overall, level_1, level_2, level_3) for a specific year and month.
    """
    if year is not None and month is not None:
        doc = await db[AGGREGATES_COLLECTION].find_one({"type": "monthly_spend", "year": year, "month": month})
        if not doc or "data" not in doc:
            return JSONResponse(
                content={"error": "No monthly spend data found for the specified year and month."}, status_code=404
            )
        return {"monthly_spend": doc["data"]}
    else:
        return JSONResponse(content={"error": "Both year and month must be specified."}, status_code=400)


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


@analytics_router.get("/analytics/weekly_spend")
async def get_weekly_spend(year: int = Query(None), week: int = Query(None)):
    """
    Returns weekly spend aggregates (overall, level_1, level_2, level_3) for a specific year and week.
    """
    if year is not None and week is not None:
        doc = await db[AGGREGATES_COLLECTION].find_one({"type": "weekly_spend", "year": year, "week": week})
        if not doc or "data" not in doc:
            return JSONResponse(
                content={"error": "No weekly spend data found for the specified year and week."}, status_code=404
            )
        return {"weekly_spend": doc["data"]}
    else:
        return JSONResponse(content={"error": "Both year and week must be specified."}, status_code=400)


@analytics_router.get("/analytics/daily_spend")
async def get_daily_spend(year: int = Query(None), month: int = Query(None)):
    """
    Returns daily spend aggregates (overall, level_1, level_2, level_3) for a specific year and month.
    """
    if year is not None and month is not None:
        doc = await db[AGGREGATES_COLLECTION].find_one({"type": "daily_spend", "year": year, "month": month})
        if not doc or "data" not in doc:
            return JSONResponse(
                content={"error": "No daily spend data found for the specified year and month."}, status_code=404
            )
        return {"daily_spend": doc["data"]}
    else:
        return JSONResponse(content={"error": "Both year and month must be specified."}, status_code=400)


@analytics_router.get("/analytics/yearly_monthly_spend")
async def get_yearly_monthly_spend(year: int = Query(...)):
    """
    Returns yearly spend per month (overall and level_1 breakdown) for a specific year.
    """
    cursor = db[AGGREGATES_COLLECTION].find({"type": "yearly_monthly_spend", "year": year})
    docs = await cursor.to_list(length=None)
    if not docs:
        return JSONResponse(content={"error": "No yearly monthly spend data found for the specified year."}, status_code=404)
    # Sort by month
    docs_sorted = sorted(docs, key=lambda d: d.get("month", 0))
    # Only return relevant fields
    result = [
        {"year": d["year"], "month": d["month"], "overall_spend": d.get("overall_spend", 0), "level_1": d.get("level_1", [])}
        for d in docs_sorted
    ]
    return {"yearly_monthly_spend": result}


@analytics_router.get("/analytics/recalculate")
async def recalculate_aggregates():
    """
    Manually trigger recalculation of all analytics aggregates (yearly, monthly, daily, weekly, yearly_monthly).
    """
    await calculate_yearly_spend()
    await calculate_monthly_spend()
    await calculate_daily_spend()
    await calculate_weekly_spend()
    await calculate_yearly_monthly_spend()
    return {"status": "ok", "message": "Recalculation ok."}
