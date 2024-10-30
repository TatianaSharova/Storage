from sqlalchemy import select
from db import db_session, ProductModel, OrderModel, OrderItemModel
from sqlalchemy.exc import IntegrityError
from schemas import ProductAdd, ProductRead, OrderAdd, OrderRead
from fastapi import HTTPException


class ProductRepository:
   '''Так как работа с одной таблицей, возьмем методы в класс.'''
   @classmethod
   async def add_product(cls, task: ProductAdd) -> int:
       async with db_session() as session:
           data = task.model_dump()
           new_product = ProductModel(**data)
           try:
               session.add(new_product)
               await session.flush()
               await session.commit()
           except IntegrityError:
               session.rollback()
               raise HTTPException(status_code=400,
                                   detail='Товар с таким названием уже существует.')
           return new_product.id

   @classmethod
   async def get_all(cls) -> list[ProductRead]:
       async with db_session() as session:
           query = select(ProductModel)
           result = await session.execute(query)
           product_models = result.scalars().all()
           products = [ProductRead.model_validate(
               product_model
            ) for product_model in product_models]
           return products
    
   @classmethod
   async def get_product(cls, product_id: int) -> ProductRead:
       async with db_session() as session:
           query = select(ProductModel).where(ProductModel.id == product_id)
           result = await session.execute(query)
           product_model = result.scalar_one_or_none()
           if product_model is None:
               raise HTTPException(status_code=404, detail='Товар не найден.')
           product = ProductRead.model_validate(product_model)
           return product


class OrderRepository:
    '''
    '''
    @classmethod
    async def add_order(cls, order: OrderAdd) -> int:
       async with db_session() as session:
        #    data = order.model_dump()
           new_order = OrderModel(status=order.status)
           session.add(new_order)
           await session.flush()

           items = order.items

           for item in items:
               query = select(ProductModel).where(ProductModel.name == item.name)
               result = await session.execute(query)
               product = result.scalar_one_or_none()
               if product is None:
                   session.rollback()
                   raise HTTPException(status_code=404, detail=f'Товар {item.name} не найден.')
               if product.in_stock < item.amount:
                   session.rollback()
                   raise HTTPException(status_code=400,
                                       detail=(f'Недостаточно {item.name} для заказа. '
                                               f'Остаток на складе - {product.in_stock}'))
               product.in_stock -= item.amount
               session.add(product)

               orderitem = OrderItemModel(order_id=new_order.id, product_id=product.id, amount=item.amount)
               session.add(orderitem)
            
           await session.flush()
           await session.commit()
           return new_order.id
    
    @classmethod
    async def get_all(cls) -> list[OrderRead]:
       async with db_session() as session:
           query = select(OrderModel)
           result = await session.execute(query)
           product_models = result.scalars().all()
           products = [OrderRead.model_validate(
               product_model
            ) for product_model in product_models]
           return products
