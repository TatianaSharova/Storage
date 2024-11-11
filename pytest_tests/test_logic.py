from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import ProductModel

from .conftest import DESCRIPTION, IN_STOCK, PRICE, PRODUCT_NAME


@pytest.mark.asyncio
async def test_unique_product_name(client: AsyncClient,
                                   async_db: AsyncSession,
                                   product: ProductModel):
    '''Нельзя создать товары с одинаковым названием.'''
    data = {'name': PRODUCT_NAME,
            'description': DESCRIPTION,
            'price': PRICE,
            'in_stock': IN_STOCK}

    response = await client.post('/products', json=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_decrease_count_in_stock(client: AsyncClient,
                                       async_db: AsyncSession,
                                       product: ProductModel):
    '''При создании заказа количество товаров в наличии уменьшается.'''
    before_in_stock = product.in_stock
    data = {
        'items': [
            {'name': product.name,
             'amount': product.in_stock}
        ]
    }

    response = await client.post('/orders', json=data)
    response_data = response.json()
    await async_db.refresh(product)
    after_in_stock = response_data['data'][
        'items'
    ][0]['amount'] - before_in_stock

    assert after_in_stock == product.in_stock == 0


@pytest.mark.asyncio
async def test_not_enough_in_stock_for_order(client: AsyncClient,
                                             async_db: AsyncSession,
                                             product: ProductModel):
    '''Нельзя создать заказ, если не хватает товара в наличии.'''
    data = {
        'items': [
            {'name': product.name,
             'amount': product.in_stock + 1}
        ]
    }

    response = await client.post('/orders', json=data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
