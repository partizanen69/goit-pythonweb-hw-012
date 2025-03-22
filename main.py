from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.routes import auth, contacts
from src.database.db import get_db


app = FastAPI()

api_prefix = "/api"
app.include_router(contacts.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)


@app.get("/")
def read_root(request: Request):
    return {"message": "TODO Application v1.0"}


@app.get(f"{api_prefix}/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
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
