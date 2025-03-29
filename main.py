"""Main application module for the Contacts API.

This module initializes the FastAPI application and sets up all necessary routes,
middleware, and configurations.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi.errors import RateLimitExceeded

from src.routes import auth, contacts, users
from src.database.db import get_db


app = FastAPI(
    title="Contacts API",
    description="A FastAPI application for managing contacts with user authentication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # FastAPI default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions.

    Args:
        request (Request): The incoming request
        exc (RateLimitExceeded): The rate limit exception

    Returns:
        JSONResponse: A 429 response with an error message
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


api_prefix = "/api"
app.include_router(contacts.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)


@app.get("/")
def read_root(request: Request):
    """Root endpoint returning application information.

    Args:
        request (Request): The incoming request

    Returns:
        dict: Application version information
    """
    return {"message": "TODO Application v1.0"}


@app.get(f"{api_prefix}/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to verify database connectivity.

    Args:
        db (AsyncSession): Database session dependency

    Returns:
        dict: Success message if database is accessible

    Raises:
        HTTPException: If database is not accessible or there's an unexpected error
    """
    try:
        result = (await db.execute(text("SELECT 1"))).scalar_one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        err_text = "Unexpected error during healthcheck call to the database"
        print(f"{err_text}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_text,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
