import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.endpoints.endpoints import router
from app.database.init_database import init_db


logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('Starting up')
    await init_db()
    yield
    logging.info('Shutting down')

app = FastAPI(lifespan=lifespan)
app.mount('/app/static', StaticFiles(directory='app/static'), name='static')
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=9000)