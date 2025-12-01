from datetime import datetime

from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    author_name = Column(String(120))
    service_rating = Column(Integer, nullable=False, default=0)
    product_rating = Column(Integer, nullable=False, default=0)
    ambience_rating = Column(Integer, nullable=False, default=0)
    recommend_rating = Column(Integer, nullable=False, default=0)
    comment = Column(Text)
    location = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship('User', backref='reviews')

    def average_score(self) -> float:
        scores = [
            self.service_rating or 0,
            self.product_rating or 0,
            self.ambience_rating or 0,
            self.recommend_rating or 0,
        ]
        return round(sum(scores) / len(scores), 1)

