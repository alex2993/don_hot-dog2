from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Table, Text
from sqlalchemy.orm import relationship

from app import db


class Category(db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    children = relationship('Category', backref='parent', remote_side=[id])


class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String(255))
    description = Column(Text)
    portion_grams = Column(Integer)
    protein_100g = Column(Numeric(7, 2))
    fat_100g = Column(Numeric(7, 2))
    carb_100g = Column(Numeric(7, 2))
    kcal_100g = Column(Integer)
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category')
    modifiers = relationship('ProductModifier', back_populates='product', cascade='all, delete-orphan')


class Modifier(db.Model):
    __tablename__ = 'modifiers'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    price_delta = Column(Numeric(10, 2), nullable=False, default=0)


class ProductModifier(db.Model):
    __tablename__ = 'product_modifiers'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    modifier_id = Column(Integer, ForeignKey('modifiers.id'))
    product = relationship('Product', back_populates='modifiers')
    modifier = relationship('Modifier')


