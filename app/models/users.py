from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    description = Column(String)
    companies = relationship('Company', back_populates='owner', cascade='all, delete')
    requests = relationship('Request', back_populates='user', cascade='all, delete')
    password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
