from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from database import engine, Base
import asyncio
import logging

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    
    max_retries = 10
    retry_delay = 2
    connected = False
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to DB.")
            connected = True
            break 
        except Exception as e:
            logger.warning(f"DB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Failed to connect to DB after retries. Exiting.")
                raise 

    if connected:
        logger.info("DB connection verified. Ready to serve requests.")
    
    yield
    
    logger.info("Shutting down...")

app = FastAPI(title="Blog API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API! DB connection OK."}