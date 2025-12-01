from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    avatar_url = Column(String(255), nullable=True)
    # Совместимость со старой схемой: используем фактическое имя колонки 'hashed_password'
    password_hash = Column('hashed_password', String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Текстовая роль для совместимости со старыми БД (NOT NULL)
    role_name = Column('role', String(50), nullable=False, server_default='staff')
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    role = relationship('Role')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


