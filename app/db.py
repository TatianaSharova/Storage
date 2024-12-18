import enum
import os
from typing import AsyncGenerator, List, Optional

from dotenv import load_dotenv
from sqlalchemy import (CheckConstraint, DateTime, Enum, Float, ForeignKey,
                        Integer, SmallInteger, String, func)
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

engine = create_async_engine(
    f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@postgres/{DB_NAME}'
)

db_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class ProductModel(Model):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(300))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    in_stock: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('in_stock >= 0', name='check_in_stock_non_negative'),
    )

    def __repr__(self) -> str:
        return self.name


class StatusModel(enum.Enum):
    PENDING = 'pending'
    SENT = 'sent'
    DELIVERED = 'delivered'


class OrderModel(Model):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    status: Mapped[StatusModel] = mapped_column(Enum(StatusModel),
                                                nullable=False,
                                                default=StatusModel.PENDING)
    items: Mapped[List['OrderItemModel']] = relationship(
        back_populates='order', lazy='selectin', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Статус заказа номер {self.id} - {self.status}.'


class OrderItemModel(Model):
    __tablename__ = 'orderitem'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('order.id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('product.id', ondelete='CASCADE'))
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped['OrderModel'] = relationship('OrderModel',
                                               back_populates='items',
                                               lazy='selectin')

    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )

    def __repr__(self) -> str:
        return f'В заказе {self.order_id} товар номер {self.product_id}.'


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_session() as session:
        try:
            yield session
        finally:
            await session.close()
