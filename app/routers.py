from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.orm_query import OrderRepository, ProductRepository
from app.schemas import OrderAdd, OrderStatusUpdate, ProductAdd

product_router = APIRouter(
    prefix='/products',
    tags=['товары']
)

order_router = APIRouter(
    prefix='/orders',
    tags=['заказы']
)


@product_router.post('', status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductAdd,
                      session: AsyncSession = Depends(get_db)):
    product_id = await ProductRepository.add_product(product, session)
    return {'data': product, 'product_id': product_id}


@product_router.get('')
async def get_products(session: AsyncSession = Depends(get_db)):
    products = await ProductRepository.get_all(session)
    return {'data': products}


@product_router.get('/{product_id}')
async def get_product(product_id: int,
                      session: AsyncSession = Depends(get_db)):
    product = await ProductRepository.get_product(product_id, session)
    return {'data': product}


@product_router.delete('/{product_id}',
                       status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int,
                         session: AsyncSession = Depends(get_db)):
    product = await ProductRepository.delete_product(product_id, session)
    return {'data': product}


@product_router.put('/{product_id}')
async def update_product(product_id: int,
                         product: ProductAdd,
                         session: AsyncSession = Depends(get_db)):
    product_id = await ProductRepository.update_product(product_id, product,
                                                        session)
    return {'data': product, 'product_id': product_id}


@order_router.post('')
async def add_order(order: OrderAdd,
                    session: AsyncSession = Depends(get_db)):
    order_id = await OrderRepository.add_order(order, session)
    return {'data': order, 'order_id': order_id}


@order_router.get('')
async def get_orders(session: AsyncSession = Depends(get_db)):
    orders = await OrderRepository.get_all(session)
    return {'data': orders}


@order_router.get('/{order_id}')
async def get_order(order_id: int, session: AsyncSession = Depends(get_db)):
    order = await OrderRepository.get_order(order_id, session)
    return {'data': order}


@order_router.patch('/{order_id}/status')
async def update_status(order_id: int, status: OrderStatusUpdate,
                        session: AsyncSession = Depends(get_db)):
    order = await OrderRepository.update_status(order_id, status, session)
    return {'data': order}
