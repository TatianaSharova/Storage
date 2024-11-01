from typing import Annotated
from fastapi import Depends, status
from fastapi import APIRouter
from app.orm_query import ProductRepository, OrderRepository

from app.schemas import ProductAdd, OrderAdd, OrderStatusUpdate

product_router = APIRouter(
   prefix='/products',
   tags=['товары'],
)

order_router = APIRouter(
   prefix='/orders',
   tags=['заказы'],
)


@product_router.post('')
async def add_product(product:Annotated[ProductAdd, Depends()]):
    product_id = await ProductRepository.add_product(product)
    return {'data': product, 'product_id': product_id}


@product_router.get('')
async def get_products():
    products = await ProductRepository.get_all()
    return {'data': products}


@product_router.get('/{product_id}')
async def get_product(product_id: int):
    product = await ProductRepository.get_product(product_id)
    return {'data': product}


@product_router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def get_product(product_id: int):
    product = await ProductRepository.delete_product(product_id)
    return {'data': product}


@product_router.put('/{product_id}')
async def update_product(product_id: int,
                         product:Annotated[ProductAdd, Depends()]):
    product_id = await ProductRepository.update_product(product_id, product)
    return {'data': product, 'product_id': product_id}


@order_router.post('')
async def add_order(order:Annotated[OrderAdd, Depends()]):
    order_id = await OrderRepository.add_order(order)
    return {'data': order, 'order_id': order_id}


@order_router.get('')
async def get_orders():
    orders = await OrderRepository.get_all()
    return {'data': orders}


@order_router.get('/{order_id}')
async def get_product(order_id: int):
    order = await OrderRepository.get_order(order_id)
    return {'data': order}


@order_router.patch('/{order_id}/status')
async def update_status(order_id: int, status:Annotated[OrderStatusUpdate, Depends()]):
    order = await OrderRepository.update_status(order_id, status)
    return {'data': order}
