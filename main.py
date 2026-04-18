from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.wordpressapi.src.routers import order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(order_router.router)