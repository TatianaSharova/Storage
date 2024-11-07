from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.db import Model, ProductModel, get_db
from app.routers import order_router, product_router

app = FastAPI()
app.include_router(product_router)
app.include_router(order_router)

engine_test = create_async_engine(
    'sqlite+aiosqlite:///test_db.db',
    # echo=True
)


test_db_session = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_db_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


PRODUCT_NAME = 'товар'
DESCRIPTION = 'описание'
PRICE = 1.0
IN_STOCK = 1
NEW_PRODUCT_NAME = 'новый товар'


@pytest_asyncio.fixture(scope='function')
async def test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield test_db_session()
    async with engine_test.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def async_db(test_db):

    async with test_db_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(scope='function')
async def client():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url='http://test') as client:
        yield client


@pytest_asyncio.fixture(scope='function')
async def product(async_db: AsyncSession) -> ProductModel:
    product = ProductModel(name=PRODUCT_NAME,
                           description=DESCRIPTION,
                           price=PRICE,
                           in_stock=IN_STOCK)
    async_db.add(product)
    await async_db.commit()
    await async_db.refresh(product)
    return product