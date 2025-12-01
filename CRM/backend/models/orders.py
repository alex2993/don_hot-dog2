from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship

from app import db


class Table(db.Model):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('tables.id'))
    status = Column(String(20), default='open')  # open, paid, cancelled
    total = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    guest_count = Column(Integer, default=1)
    waiter = Column(String(120))
    comment = Column(String(255))
    table = relationship('Table')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    product_name = Column(String(200), nullable=False)
    qty = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    sum = Column(Numeric(10, 2), nullable=False)
    order = relationship('Order', back_populates='items')


class Payment(db.Model):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String(30), default='cash')  # cash, card, online
    created_at = Column(DateTime, default=datetime.utcnow)


class DeliveryOrder(db.Model):
    __tablename__ = 'delivery_orders'
    id = Column(Integer, primary_key=True)
    status = Column(String(20), default='new')  # new, in_progress, done, cancelled
    source = Column(String(30), default='phone')  # phone, site, aggregator
    phone = Column(String(30))
    customer_name = Column(String(120))
    street = Column(String(200))
    house = Column(String(50))
    flat = Column(String(50))
    entrance = Column(String(50))
    floor = Column(String(50))
    comment = Column(String(255))
    planned_at = Column(DateTime)
    receive_method = Column(String(20), default='delivery')  # delivery, pickup, dinein
    payment_type = Column(String(20), default='cash')
    total = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    courier_id = Column(Integer)  # Employee.id (courier)
    user_id = Column(Integer, ForeignKey('users.id'))
    items = relationship('DeliveryOrderItem', back_populates='order', cascade='all, delete-orphan')
    user = relationship('User', backref='delivery_orders')


class DeliveryOrderItem(db.Model):
    __tablename__ = 'delivery_order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('delivery_orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    product_name = Column(String(200), nullable=False)
    qty = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    sum = Column(Numeric(10, 2), nullable=False)
    order = relationship('DeliveryOrder', back_populates='items')


