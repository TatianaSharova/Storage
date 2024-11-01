from sqlalchemy import select
from app.db import db_session, ProductModel, OrderModel, OrderItemModel
from sqlalchemy.exc import IntegrityError
from app.schemas import ProductAdd, ProductRead, OrderAdd, OrderRead, OrderStatusUpdate
from fastapi import HTTPException


class ProductRepository:
    '''Методы для работы с товарами.'''
    @classmethod
    async def add_product(cls, product: ProductAdd) -> int:
        async with db_session() as session:
            data = product.model_dump()
            new_product = ProductModel(**data)
            try:
                session.add(new_product)
                await session.commit()
            except IntegrityError:
                await session.rollback()
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

    @classmethod
    async def delete_product(cls, product_id: int) -> None:
        async with db_session() as session:
            query = select(ProductModel).where(ProductModel.id == product_id)
            result = await session.execute(query)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                raise HTTPException(status_code=404, detail='Товар не найден.')
            await session.delete(product_model)
            await session.commit()
            return
    
    @classmethod
    async def update_product(cls, product_id: int,
                             product: ProductAdd) -> ProductRead:
        async with db_session() as session:
            query = select(ProductModel).where(ProductModel.id == product_id)
            result = await session.execute(query)
            product_model = result.scalar_one_or_none()
            if product_model is None:
                raise HTTPException(status_code=404, detail='Товар не найден.')
            
            for key, value in product.model_dump().items():
                setattr(product_model, key, value)
        
            session.add(product_model)
            await session.commit()
            return product_model.id


class OrderRepository:
    '''Методы для работы с заказами.'''
    @classmethod
    async def add_order(cls, order: OrderAdd) -> int:
       async with db_session() as session:
           new_order = OrderModel(status=order.status)
           session.add(new_order)
           await session.flush()

           items = order.items

           for item in items:
               query = select(ProductModel).where(ProductModel.name == item.name)
               result = await session.execute(query)
               product = result.scalar_one_or_none()
               if product is None:
                   raise HTTPException(status_code=404, detail=f'Товар {item.name} не найден.')
               if product.in_stock < item.amount:
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
           order_models = result.scalars().all()
           orders = [OrderRead.model_validate(
               order_model
            ) for order_model in order_models]
           return orders
    
    @classmethod
    async def get_order(cls, order_id: int) -> OrderRead:
       async with db_session() as session:
           query = select(OrderModel).where(OrderModel.id == order_id)
           result = await session.execute(query)
           order_model = result.scalar_one_or_none()

           if order_model is None:
               raise HTTPException(status_code=404, detail='Заказ не найден.')
           order = OrderRead.model_validate(order_model)
           return order
    
    @classmethod
    async def update_status(cls, order_id: int,
                            status: OrderStatusUpdate) -> OrderRead:
       async with db_session() as session:
           query = select(OrderModel).where(OrderModel.id == order_id)
           result = await session.execute(query)
           order_model = result.scalar_one_or_none()
           if order_model is None:
               raise HTTPException(status_code=404, detail='Заказ не найден.')
           
           order_model.status = status.status
           session.add(order_model)
           await session.flush()
           await session.commit()
           order = OrderRead.model_validate(order_model)
           return order
