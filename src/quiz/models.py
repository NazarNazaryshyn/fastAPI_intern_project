import datetime as datetime
from sqlalchemy.orm import relationship, backref

from src.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, Date

import datetime

class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    questions = relationship("Question", backref=backref("quiz", lazy="joined"))


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'))
    question = Column(String, nullable=False)
    variants = relationship("AnswerVariant", backref=backref("question", lazy="joined"))

    
class AnswerVariant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'))
    correct_answers = Column(Integer)
    all_answers = Column(Integer)
    gpa = Column(Float)
    datetime = Column(Date, default=datetime.datetime.now, nullable=False)
