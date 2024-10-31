from typing import Optional, List
import datetime as dt
from db import StatusModel
from pydantic import BaseModel, ConfigDict, Field


class ProductAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=40, description='Название товара')
    description: Optional[str] = Field(None, max_length=300, description='Описание товара')
    price: float = Field(..., gt=0, description='Цена должна быть больше 0')
    in_stock: int = Field(
        ..., ge=0, description='Наличие должно быть больше или равно 0')


class ProductRead(ProductAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=40, description='Название товара')
    amount: int = Field(..., gt=0, description='Количество товаров')
    model_config = ConfigDict(from_attributes=True)


class OrderAdd(BaseModel):
    items: List[Item]
    status: Optional[StatusModel] = Field(StatusModel.PENDING, description='Статус заказа')


class OrderItemRead(BaseModel):
    product_id: int
    amount: int
    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    status: StatusModel
    created: dt.datetime
    items: List[OrderItemRead]
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: StatusModel


