from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import OrderModel, ProductModel, StatusModel

from .conftest import (DESCRIPTION, IN_STOCK, NEW_PRODUCT_NAME, NEW_STATUS,
                       PRICE, PRODUCT_NAME)


@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient, async_db: AsyncSession,
                                 product: ProductModel) -> None:
    '''Проверка на получение товара по id.'''
    response = await client.get(f'/products/{product.id}')
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_data['data']['id'] == product.id


@pytest.mark.asyncio
async def test_get_products(client: AsyncClient, async_db: AsyncSession,
                            product: ProductModel):
    '''Проверка на получение списка товаров.'''
    response = await client.get('/products')
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert isinstance(data['data'], list)
    assert len(data['data']) == 1


@pytest.mark.asyncio
async def test_add_product(client: AsyncClient, async_db: AsyncSession):
    '''Проверка на создание товара.'''
    data = {'name': PRODUCT_NAME,
            'description': DESCRIPTION,
            'price': PRICE,
            'in_stock': IN_STOCK}

    response = await client.post('/products', json=data)

    response_data = response.json()
    assert response.status_code == HTTPStatus.CREATED
    assert response_data['data']['name'] == PRODUCT_NAME
    assert response_data['data']['description'] == DESCRIPTION
    assert response_data['data']['price'] == PRICE
    assert response_data['data']['in_stock'] == IN_STOCK


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, async_db: AsyncSession,
                              product: ProductModel):
    '''Проверка на удаление товара.'''
    query = select(ProductModel)
    result = await async_db.execute(query)
    product_models = result.scalars().all()
    before_deleting = len(product_models)

    response = await client.delete(f'/products/{product.id}')

    query = select(ProductModel)
    result = await async_db.execute(query)
    product_models = result.scalars().all()
    after_deleting = len(product_models)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert before_deleting == 1
    assert after_deleting == 0


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, async_db: AsyncSession,
                              product: ProductModel):
    '''Проверка на изменение товара.'''

    data = {
        'name': NEW_PRODUCT_NAME,
        'description': DESCRIPTION,
        'price': PRICE,
        'in_stock': IN_STOCK
    }

    response = await client.put(f'/products/{product.id}', json=data)

    query = select(ProductModel).where(ProductModel.id == product.id)
    result = await async_db.execute(query)
    new_product = result.scalar_one_or_none()
    await async_db.refresh(new_product)

    assert response.status_code == HTTPStatus.OK
    assert new_product.name == NEW_PRODUCT_NAME


@pytest.mark.asyncio
async def test_add_order(client: AsyncClient, async_db: AsyncSession,
                         product: ProductModel):
    '''Проверка на создание заказа.'''
    data = {
        'items': [
            {'name': product.name,
             'amount': product.in_stock}
        ]
    }

    response = await client.post('/orders', json=data)

    response_data = response.json()
    assert response.status_code == HTTPStatus.CREATED
    assert response_data['data']['items'][0]['name'] == product.name
    assert response_data['data']['items'][0]['amount'] == product.in_stock


@pytest.mark.asyncio
async def test_get_order_by_id(client: AsyncClient, async_db: AsyncSession,
                               order: OrderModel) -> None:
    '''Проверка на получение товара по id.'''
    response = await client.get(f'/orders/{order.id}')
    response_data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_data['data']['id'] == order.id


@pytest.mark.asyncio
async def test_get_orders(client: AsyncClient, async_db: AsyncSession,
                          order: OrderModel) -> None:
    '''Проверка на получение списка заказов.'''
    response = await client.get('/orders')
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert isinstance(data['data'], list)
    assert len(data['data']) == 1


@pytest.mark.asyncio
async def test_update_status(client: AsyncClient, async_db: AsyncSession,
                             order: OrderModel) -> None:
    '''Проверка на изменение статуса заказа.'''
    data = {'status': NEW_STATUS}
    response = await client.patch(f'/orders/{order.id}/status',
                                  json=data)

    updated_order = response.json()

    query = select(OrderModel).where(OrderModel.id == order.id)
    result = await async_db.execute(query)
    new_order = result.scalar_one_or_none()
    await async_db.refresh(new_order)

    assert response.status_code == HTTPStatus.OK
    assert updated_order['data']['status'] == NEW_STATUS
    assert new_order.status == StatusModel.SENT
