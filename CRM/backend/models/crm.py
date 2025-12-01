from sqlalchemy import Column, Integer, String, Numeric
from app import db


class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True)
    name = Column(String(120))
    points = Column(Integer, default=0)
    tier_id = Column(Integer)


class LoyaltyTier(db.Model):
    __tablename__ = 'loyalty_tiers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    discount_percent = Column(Numeric(5, 2), default=0)


class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(200))
    discount_percent = Column(Numeric(5, 2), default=0)


class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    desired_position = Column(String(120))
    city = Column(String(120))
    phone = Column(String(50))
    email = Column(String(120))
    comment = Column(String(500))


