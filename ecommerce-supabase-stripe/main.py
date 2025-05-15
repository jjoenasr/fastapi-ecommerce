from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from contextlib import asynccontextmanager
from routes.auth import router as auth_router
from routes.store import router as store_router
from routes.chat import router as chat_router
from logger_config import logger
import os
import uvicorn
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan,
            title=settings.app_name,
            description=settings.app_description,
            version=settings.app_version)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for HTTPException
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error. Please try again later."},
    )

# Include the routes
app.include_router(auth_router)
app.include_router(store_router)
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run("main:app", log_level="info", reload=True)