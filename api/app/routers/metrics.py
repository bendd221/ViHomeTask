from fastapi import APIRouter, Query, HTTPException
from services.athena_service import AsyncAthenaService
from loguru import logger

router = APIRouter(prefix="/metrics")
athena_service = AsyncAthenaService()


@router.get("/average-daily-return")
async def daily_average_return(
    from_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    logger.info(f"Fetching average-daily-return from {from_date} to {to_date}")
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date cannot be after to_date")

    query = f"""
    SELECT
        date,
        average_return
    FROM average_daily_returns
    WHERE date BETWEEN DATE '{from_date}' AND DATE '{to_date}'
    ORDER BY date ASC
    """
    
    logger.debug(f"Starting Athena Query Execution")
    results = await athena_service.execute(query)
    logger.info("Results retreived sucessfully")
    return results


@router.get("/most-valuable-day")
async def highest_average_traded_value_day():
    return await athena_service.execute("""
        SELECT * from highest_average_traded_value
        """
    )


@router.get("/most-volatile")
async def most_volatile_stock():
    return await athena_service.execute("""
        SELECT * from most_volatile_stock
        """
    )