from datetime import date, datetime, time
from sqlalchemy import Column, Integer, String, Date, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Employee(db.Model):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    position = Column(String(120), nullable=False)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    shifts = relationship('Shift', back_populates='employee', cascade='all, delete-orphan')


class Shift(db.Model):
    __tablename__ = 'shifts'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    day = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    employee = relationship('Employee', back_populates='shifts')




