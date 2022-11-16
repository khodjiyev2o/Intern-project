from typing import Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class CompanyCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    visible: Optional[bool]


class CompanyAlterSchema(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    visible: Optional[bool]


class CompanySchema(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=32)
    owner: str = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    visible: bool


class MemberSchema(BaseModel):
    company: str = Field(min_length=1, max_length=32)
    user: str = Field(min_length=1, max_length=32)
    admin: Optional[bool]


class RequestSchema(BaseModel):
    id: int = Field(gt=0)
    user: str = Field(min_length=1, max_length=32)
    company: str = Field(min_length=1, max_length=32)
    side: Literal['Company invites user', 'User requests access to company']


class QuizCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    frequency: int = Field(gt=0)
    questions: list[str] = Field(min_length=1, max_length=16384)
    answer_options: list[list[str]] = Field(min_length=1, max_length=65536)
    correct_answers: list[int]

    @validator('correct_answers')
    def validate_quiz(cls, value, values):
        if len(values['questions']) < 2:
            raise ValueError('Invalid quiz!')
        for option in values['answer_options']:
            if len(option) < 2:
                raise ValueError('Invalid quiz!')
        if len(value) != len(values['questions']) != len(values['answer_options']):
            raise ValueError('Invalid quiz!')
        for options, answer in zip(values['answer_options'], value):
            if answer > len(options):
                raise ValueError('Invalid quiz!')
        return value


class QuizAlterSchema(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    frequency: Optional[int] = Field(gt=0)
    questions: Optional[list[str]] = Field(min_length=1, max_length=16384)
    answer_options: Optional[list[list[str]]] = Field(min_length=1, max_length=65536)
    correct_answers: Optional[list[int]]

    @validator('correct_answers')
    def validate_quiz(cls, value, values):
        if not value and not values['questions'] and not values['answer_options']:
            return value
        if not value or not values['questions'] or not values['answer_options']:
            if value != values['questions'] != values['answer_options'] != None:
                raise ValueError('Invalid quiz!')
        if len(values['questions']) < 2:
            raise ValueError('Invalid quiz!')
        for option in values['answer_options']:
            if len(option) < 2:
                raise ValueError('Invalid quiz!')
        if len(value) != len(values['questions']) != len(values['answer_options']):
            raise ValueError('Invalid quiz!')
        for options, answer in zip(values['answer_options'], value):
            if answer > len(options):
                raise ValueError('Invalid quiz!')
        return value


class QuizSchema(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(min_length=1, max_length=4096)
    frequency: int = Field(gt=0)
    quiz: dict


class QuizAnswerSchema(BaseModel):
    answers: list[int]


class ResultSchema(BaseModel):
    id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    quiz_id: int = Field(gt=0)
    company_id: int = Field(gt=0)
    overall_questions: int = Field(gt=0)
    correct_answers: int = Field(ge=0)


class AverageScoreSchema(BaseModel):
    date: str
    average_score: float = Field(ge=0)


class AverageScoreUserSchema(BaseModel):
    user_id: int
    average_score: float = Field(ge=0)


class LastTimeQuiz(BaseModel):
    user_id: int = Field(gt=0)
    quiz_id: int = Field(gt=0)
    last_time: str
