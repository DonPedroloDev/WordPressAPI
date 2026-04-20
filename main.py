from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from src.wordpressapi.src.routers import order_router
from src.wordpressapi.src.routers import odoo_woocommerce_router
from src.wordpressapi.src.routers import sync_orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(order_router.router)
app.include_router(odoo_woocommerce_router.router)
app.include_router(sync_orders.router)