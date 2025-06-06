import logging
import os
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DATABASE", "receipts")
RECEIPTS_COLLECTION = "receipts"
AGGREGATES_COLLECTION = "aggregates"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

logger = logging.getLogger(__name__)

logger.info(f"Async MongoDB client connected to {MONGO_URI} and database {DB_NAME}")


async def calculate_monthly_spend():
    logger.info("Calculating monthly spend...")
    # Project receipt_data.date and receipt_data.total to root for grouping
    overall_pipeline = [
        {"$project": {"date": "$receipt_data.date", "total": "$receipt_data.total"}},
        {"$group": {"_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}}, "total_spend": {"$sum": "$total"}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    overall = await db[RECEIPTS_COLLECTION].aggregate(overall_pipeline).to_list(length=None)

    level1_pipeline = [
        {"$unwind": "$items"},
        {"$project": {"date": "$receipt_data.date", "level_1": "$items.item_category.level_1", "total": "$items.total_price"}},
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}, "level_1": "$level_1"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.level_1": 1}},
    ]
    level1 = await db[RECEIPTS_COLLECTION].aggregate(level1_pipeline).to_list(length=None)

    level2_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_1": "$items.item_category.level_1",
                "level_2": "$items.item_category.level_2",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "level_1": "$level_1",
                    "level_2": "$level_2",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.level_1": 1, "_id.level_2": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_1": "$__id.level_1", "level_2": "$__id.level_2"}},
    ]
    level2 = await db[RECEIPTS_COLLECTION].aggregate(level2_pipeline).to_list(length=None)

    level3_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_2": "$items.item_category.level_2",
                "level_3": "$items.item_category.level_3",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "level_2": "$level_2",
                    "level_3": "$level_3",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.level_2": 1, "_id.level_3": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_2": "$__id.level_2", "level_3": "$__id.level_3"}},
    ]
    level3 = await db[RECEIPTS_COLLECTION].aggregate(level3_pipeline).to_list(length=None)

    # Organize by (year, month)
    from collections import defaultdict

    monthly_data = defaultdict(lambda: {"overall": [], "level_1": [], "level_2": [], "level_3": []})
    for entry in overall:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_data[(y, m)]["overall"].append(entry)
    for entry in level1:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_data[(y, m)]["level_1"].append(entry)
    for entry in level2:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_data[(y, m)]["level_2"].append(entry)
    for entry in level3:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_data[(y, m)]["level_3"].append(entry)

    # Store or update one document per (year, month)
    for (y, m), data in monthly_data.items():
        await db[AGGREGATES_COLLECTION].update_one(
            {"type": "monthly_spend", "year": y, "month": m},
            {"$set": {"data": data, "last_updated": datetime.utcnow()}},
            upsert=True,
        )
    logger.info("Monthly spend calculation complete.")


async def calculate_daily_spend():
    logger.info("Calculating daily spend...")
    # Overall daily totals
    overall_pipeline = [
        {"$project": {"date": "$receipt_data.date", "total": "$receipt_data.total"}},
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}, "day": {"$dayOfMonth": "$date"}},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
    ]
    overall = await db[RECEIPTS_COLLECTION].aggregate(overall_pipeline).to_list(length=None)

    # Daily totals per level_1 item type
    level1_pipeline = [
        {"$unwind": "$items"},
        {"$project": {"date": "$receipt_data.date", "level_1": "$items.item_category.level_1", "total": "$items.total_price"}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "day": {"$dayOfMonth": "$date"},
                    "level_1": "$level_1",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.level_1": 1}},
    ]
    level1 = await db[RECEIPTS_COLLECTION].aggregate(level1_pipeline).to_list(length=None)

    # Daily totals per level_2 item type
    level2_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_1": "$items.item_category.level_1",
                "level_2": "$items.item_category.level_2",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "day": {"$dayOfMonth": "$date"},
                    "level_1": "$level_1",
                    "level_2": "$level_2",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.level_1": 1, "_id.level_2": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_1": "$_id.level_1", "level_2": "$_id.level_2"}},
    ]
    level2 = await db[RECEIPTS_COLLECTION].aggregate(level2_pipeline).to_list(length=None)

    # Daily totals per level_3 item type
    level3_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_2": "$items.item_category.level_2",
                "level_3": "$items.item_category.level_3",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "day": {"$dayOfMonth": "$date"},
                    "level_2": "$level_2",
                    "level_3": "$level_3",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1, "_id.level_2": 1, "_id.level_3": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_2": "$_id.level_2", "level_3": "$_id.level_3"}},
    ]
    level3 = await db[RECEIPTS_COLLECTION].aggregate(level3_pipeline).to_list(length=None)

    # Organize by (year, month)
    from collections import defaultdict

    daily_data = defaultdict(lambda: {"overall": [], "level_1": [], "level_2": [], "level_3": []})
    for entry in overall:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        daily_data[(y, m)]["overall"].append(entry)
    for entry in level1:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        daily_data[(y, m)]["level_1"].append(entry)
    for entry in level2:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        daily_data[(y, m)]["level_2"].append(entry)
    for entry in level3:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        daily_data[(y, m)]["level_3"].append(entry)

    # Store or update one document per (year, month)
    for (y, m), data in daily_data.items():
        await db[AGGREGATES_COLLECTION].update_one(
            {"type": "daily_spend", "year": y, "month": m},
            {"$set": {"data": data, "last_updated": datetime.utcnow()}},
            upsert=True,
        )
    logger.info("Daily spend calculation complete.")


async def calculate_yearly_spend():
    logger.info("Calculating yearly spend...")
    # Overall yearly totals
    overall_pipeline = [
        {"$project": {"year": {"$year": "$receipt_data.date"}, "total": "$receipt_data.total"}},
        {"$group": {"_id": {"year": "$year"}, "total_spend": {"$sum": "$total"}}},
        {"$sort": {"_id.year": 1}},
    ]
    overall = await db[RECEIPTS_COLLECTION].aggregate(overall_pipeline).to_list(length=None)

    # Yearly totals per level_1 item type
    level1_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "year": {"$year": "$receipt_data.date"},
                "level_1": "$items.item_category.level_1",
                "total": "$items.total_price",
            }
        },
        {"$group": {"_id": {"year": "$year", "level_1": "$level_1"}, "total_spend": {"$sum": "$total"}}},
        {"$sort": {"_id.year": 1, "_id.level_1": 1}},
    ]
    level1 = await db[RECEIPTS_COLLECTION].aggregate(level1_pipeline).to_list(length=None)

    # Yearly totals per level_2 item type
    level2_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "year": {"$year": "$receipt_data.date"},
                "level_1": "$items.item_category.level_1",
                "level_2": "$items.item_category.level_2",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "level_1": "$level_1", "level_2": "$level_2"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.level_1": 1, "_id.level_2": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_1": "$_id.level_1", "level_2": "$_id.level_2"}},
    ]
    level2 = await db[RECEIPTS_COLLECTION].aggregate(level2_pipeline).to_list(length=None)

    # Yearly totals per level_3 item type
    level3_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "year": {"$year": "$receipt_data.date"},
                "level_2": "$items.item_category.level_2",
                "level_3": "$items.item_category.level_3",
                "total": "$items.total_price",
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "level_2": "$level_2", "level_3": "$level_3"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.level_2": 1, "_id.level_3": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_2": "$_id.level_2", "level_3": "$_id.level_3"}},
    ]
    level3 = await db[RECEIPTS_COLLECTION].aggregate(level3_pipeline).to_list(length=None)

    # Store or update the aggregates in a separate collection
    await db[AGGREGATES_COLLECTION].update_one(
        {"type": "yearly_spend"},
        {
            "$set": {
                "data": {"overall": overall, "level_1": level1, "level_2": level2, "level_3": level3},
                "last_updated": datetime.utcnow(),
            }
        },
        upsert=True,
    )
    logger.info("Yearly spend calculation complete.")


async def calculate_weekly_spend():
    logger.info("Calculating weekly spend...")
    # Overall weekly totals
    overall_pipeline = [
        {
            "$project": {
                "date": "$receipt_data.date",
                "total": "$receipt_data.total",
                "year": {"$isoWeekYear": "$receipt_data.date"},
                "week": {"$isoWeek": "$receipt_data.date"},
                "first_day_of_week": {
                    "$dateFromParts": {
                        "isoWeekYear": {"$isoWeekYear": "$receipt_data.date"},
                        "isoWeek": {"$isoWeek": "$receipt_data.date"},
                        "isoDayOfWeek": 1,
                    }
                },
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "week": "$week", "first_day_of_week": "$first_day_of_week"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.week": 1}},
    ]
    overall = await db[RECEIPTS_COLLECTION].aggregate(overall_pipeline).to_list(length=None)

    # Weekly totals per level_1 item type
    level1_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_1": "$items.item_category.level_1",
                "total": "$items.total_price",
                "year": {"$isoWeekYear": "$receipt_data.date"},
                "week": {"$isoWeek": "$receipt_data.date"},
                "first_day_of_week": {
                    "$dateFromParts": {
                        "isoWeekYear": {"$isoWeekYear": "$receipt_data.date"},
                        "isoWeek": {"$isoWeek": "$receipt_data.date"},
                        "isoDayOfWeek": 1,
                    }
                },
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "week": "$week", "level_1": "$level_1", "first_day_of_week": "$first_day_of_week"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.week": 1, "_id.level_1": 1}},
    ]
    level1 = await db[RECEIPTS_COLLECTION].aggregate(level1_pipeline).to_list(length=None)

    # Weekly totals per level_2 item type
    level2_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_1": "$items.item_category.level_1",
                "level_2": "$items.item_category.level_2",
                "total": "$items.total_price",
                "year": {"$isoWeekYear": "$receipt_data.date"},
                "week": {"$isoWeek": "$receipt_data.date"},
                "first_day_of_week": {
                    "$dateFromParts": {
                        "isoWeekYear": {"$isoWeekYear": "$receipt_data.date"},
                        "isoWeek": {"$isoWeek": "$receipt_data.date"},
                        "isoDayOfWeek": 1,
                    }
                },
            }
        },
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "week": "$week",
                    "level_1": "$level_1",
                    "level_2": "$level_2",
                    "first_day_of_week": "$first_day_of_week",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.week": 1, "_id.level_1": 1, "_id.level_2": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_1": "$_id.level_1", "level_2": "$_id.level_2"}},
    ]
    level2 = await db[RECEIPTS_COLLECTION].aggregate(level2_pipeline).to_list(length=None)

    # Weekly totals per level_3 item type
    level3_pipeline = [
        {"$unwind": "$items"},
        {
            "$project": {
                "date": "$receipt_data.date",
                "level_2": "$items.item_category.level_2",
                "level_3": "$items.item_category.level_3",
                "total": "$items.total_price",
                "year": {"$isoWeekYear": "$receipt_data.date"},
                "week": {"$isoWeek": "$receipt_data.date"},
                "first_day_of_week": {
                    "$dateFromParts": {
                        "isoWeekYear": {"$isoWeekYear": "$receipt_data.date"},
                        "isoWeek": {"$isoWeek": "$receipt_data.date"},
                        "isoDayOfWeek": 1,
                    }
                },
            }
        },
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "week": "$week",
                    "level_2": "$level_2",
                    "level_3": "$level_3",
                    "first_day_of_week": "$first_day_of_week",
                },
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.week": 1, "_id.level_2": 1, "_id.level_3": 1}},
        {"$project": {"_id": 1, "total_spend": 1, "level_2": "$_id.level_2", "level_3": "$_id.level_3"}},
    ]
    level3 = await db[RECEIPTS_COLLECTION].aggregate(level3_pipeline).to_list(length=None)

    # Organize by (year, week)
    from collections import defaultdict

    weekly_data = defaultdict(lambda: {"overall": [], "level_1": [], "level_2": [], "level_3": []})
    for entry in overall:
        y, w = entry["_id"]["year"], entry["_id"]["week"]
        weekly_data[(y, w)]["overall"].append(entry)
    for entry in level1:
        y, w = entry["_id"]["year"], entry["_id"]["week"]
        weekly_data[(y, w)]["level_1"].append(entry)
    for entry in level2:
        y, w = entry["_id"]["year"], entry["_id"]["week"]
        weekly_data[(y, w)]["level_2"].append(entry)
    for entry in level3:
        y, w = entry["_id"]["year"], entry["_id"]["week"]
        weekly_data[(y, w)]["level_3"].append(entry)

    # Store or update one document per (year, week)
    for (y, w), data in weekly_data.items():
        await db[AGGREGATES_COLLECTION].update_one(
            {"type": "weekly_spend", "year": y, "week": w},
            {"$set": {"data": data, "last_updated": datetime.utcnow()}},
            upsert=True,
        )
    logger.info("Weekly spend calculation complete.")


#
# Generates the following document:
#
# - year
# - month
# - overall_spend
# - list of level_1 data
# { "level_1", "Groceries", "total_spend": 100 }
# { "level_1", "Household items", "total_spend": 50 }
# (for as many level_1 items as we have)
#
async def calculate_yearly_monthly_spend():
    logger.info("Calculating yearly-monthly spend...")
    # Overall monthly totals per year
    overall_pipeline = [
        {"$project": {"date": "$receipt_data.date", "total": "$receipt_data.total"}},
        {"$group": {"_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}}, "total_spend": {"$sum": "$total"}}},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    overall = await db[RECEIPTS_COLLECTION].aggregate(overall_pipeline).to_list(length=None)

    # Monthly totals per level_1 per year
    level1_pipeline = [
        {"$unwind": "$items"},
        {"$project": {"date": "$receipt_data.date", "level_1": "$items.item_category.level_1", "total": "$items.total_price"}},
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}, "level_1": "$level_1"},
                "total_spend": {"$sum": "$total"},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.level_1": 1}},
    ]
    level1 = await db[RECEIPTS_COLLECTION].aggregate(level1_pipeline).to_list(length=None)

    # Organize by (year, month)
    from collections import defaultdict

    monthly_docs = defaultdict(lambda: {"overall_spend": 0, "level_1": []})
    for entry in overall:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_docs[(y, m)]["overall_spend"] = entry["total_spend"]
    for entry in level1:
        y, m = entry["_id"]["year"], entry["_id"]["month"]
        monthly_docs[(y, m)]["level_1"].append({"level_1": entry["_id"]["level_1"], "total_spend": entry["total_spend"]})

    # Store or update one document per (year, month)
    for (y, m), data in monthly_docs.items():
        await db[AGGREGATES_COLLECTION].update_one(
            {"type": "yearly_monthly_spend", "year": y, "month": m},
            {
                "$set": {
                    "year": y,
                    "month": m,
                    "overall_spend": data["overall_spend"],
                    "level_1": data["level_1"],
                    "last_updated": datetime.utcnow(),
                }
            },
            upsert=True,
        )
    logger.info("Yearly-monthly spend calculation complete.")


async def listen_for_receipt_changes():
    logger.info("Listening for changes in the receipts collection...")
    try:
        async with db[RECEIPTS_COLLECTION].watch() as change_stream:
            async for change in change_stream:
                logger.info(f"Change detected in receipts collection: {change}")
                try:
                    await calculate_monthly_spend()
                    await calculate_daily_spend()
                    await calculate_yearly_spend()
                    await calculate_weekly_spend()
                    await calculate_yearly_monthly_spend()
                except Exception as e:
                    logger.error(f"Error in aggregation functions: {e}")
    except Exception as e:
        logger.error(f"Error in listen_for_receipt_changes: {e}")
