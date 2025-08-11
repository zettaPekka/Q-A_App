import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.endpoints.post_endpoints import router as post_endpoint
from app.endpoints.page_endpoints import router as page_router
from app.endpoints.auth_endpoints import router as auth_endpoint
from app.database.init_database import init_db


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    await init_db()
    yield
    logging.info("Shutting down")


app = FastAPI(lifespan=lifespan)  # TODO: openapi_url=None docs_url=none redoc_url=none
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
app.include_router(post_endpoint)
app.include_router(auth_endpoint)
app.include_router(page_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000)
