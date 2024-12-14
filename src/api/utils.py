from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    A health check endpoint for verifying the application's connectivity to the database.

    This endpoint attempts a simple SQL query ("SELECT 1") to ensure that the database connection is functional.
    If the query succeeds and returns a result, the service is considered healthy.

    Args:
        db (AsyncSession): The asynchronous database session provided by the dependency injection.

    Raises:
        HTTPException: If the database is not configured correctly or cannot be reached, returns a 500 error.

    Returns:
        dict: A success message indicating that the application is running and connected to the database.
    """
    try:
        # Execute an asynchronous query
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
