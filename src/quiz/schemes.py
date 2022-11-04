from typing import Optional, List
from pydantic import BaseModel


class QuizSchema(BaseModel):
    title: Optional[str]
    description: Optional[str]
    frequency: Optional[int]

    class Config:
        orm_mode = True


class QuestionSchema(BaseModel):
    question: str
    quiz_id: int

    class Config:
        orm_mode = True


class VariantSchema(BaseModel):
    answer: Optional[str]
    is_correct: Optional[bool]

    class Config:
        orm_mode = True


class QuizWithQuestion(BaseModel):
    company_id: int
    title: str
    description: str
    frequency: int
    questions: list

    class Config:
        orm_mode = True


class TakeQuiz(BaseModel):
    quiz_id: int
    company_id: int
    answers: List[str]

    class Config:
        orm_mode = True


class GpaScheme(BaseModel):
    gpa: float

    class Config:
        orm_mode = True


class QuizResScheme(BaseModel):
    all_answers: int
    correct_answers: int

    class Config:
        orm_mode = True


class QuizResults(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    correct_answers: int
    all_answers: int
    gpa: float

    class Config:
        orm_mode = True