from typing import Annotated
from fastapi import Depends
from fastapi import APIRouter
from orm_query import ProductRepository, OrderRepository

from schemas import ProductAdd, OrderAdd

product_router = APIRouter(
   prefix='/products',
   tags=['задачи'],
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

@order_router.post('')
async def add_order(order:Annotated[OrderAdd, Depends()]):
    order_id = await OrderRepository.add_order(order)
    return {'data': order, 'order_id': order_id}

@order_router.get('')
async def get_orders():
    orders = await OrderRepository.get_all()
    return {'data': orders}