from fastapi import APIRouter, Query, HTTPException
from services.athena_service import AsyncAthenaService
from loguru import logger

router = APIRouter(prefix="/metrics")
athena_service = AsyncAthenaService()


@router.get("/daily-average-return")
async def daily_average_return(
    from_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    logger.info(f"Entering endpoint 'average-daily-return with dates {from_date} to {to_date}'") 
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date cannot be after to_date")

    query = f"""
    SELECT
        date,
        average_return
    FROM average_daily_return
    WHERE date BETWEEN DATE '{from_date}' AND DATE '{to_date}'
    ORDER BY date ASC
    """
    
    results = await athena_service.execute(query)
    return results


@router.get("/most-valuable-day")
async def highest_average_traded_value_day():
    logger.info(f"Entering endpoint 'most-valuable-day'") 
    return await athena_service.execute("""
        SELECT * from highest_average_traded_value
        """
    )


@router.get("/most-volatile")
async def most_volatile_stock():
    logger.info(f"Entering endpoint 'most-volatile'") 
    return await athena_service.execute("""
        SELECT * from most_volatile_stock
        """
    )