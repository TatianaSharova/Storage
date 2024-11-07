from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_table, delete_tables
from app.routers import order_router, product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_table()
    print('good')
    yield
    print('end')

app = FastAPI(lifespan=lifespan)


app.include_router(product_router)
app.include_router(order_router)
