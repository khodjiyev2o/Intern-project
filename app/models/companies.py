from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import relationship
from db import Base


class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    owner = relationship('User', back_populates='companies')
    description = Column(String)
    visible = Column(Boolean, default=True)
    requests = relationship('Request', back_populates='company', cascade='all, delete')
    quizzes = relationship('Quiz', back_populates='company', cascade='all, delete')
    members = relationship('Member', back_populates='company', cascade='all, delete')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Member(Base):
    __tablename__ = 'members'
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True)
    company = relationship('Company', back_populates='members')
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    admin = Column(Boolean, default=False)


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship('User', back_populates='requests')
    company_id = Column(Integer, ForeignKey('companies.id'), index=True)
    company = relationship('Company', back_populates='requests')
    side = Column(Boolean)


class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    frequency = Column(Integer)
    quiz = Column(JSON)
    company_id = Column(Integer, ForeignKey('companies.id'), index=True)
    company = relationship('Company', back_populates='quizzes')


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), index=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), index=True)
    overall_questions = Column(Integer)
    correct_answers = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
