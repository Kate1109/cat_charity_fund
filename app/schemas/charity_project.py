from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, validator, Extra


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[PositiveInt] = Field(None)


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default=..., min_length=1)
    full_amount: PositiveInt


class CharityProjectDB(CharityProjectCreate):
    id: int = Field(...,)
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)
    create_date: datetime = Field(...,)
    close_date: Optional[datetime] = Field(None)

    class Config:
        orm_mode = True


class CharityProjectUpdate(CharityProjectBase):
    @validator('name')
    def name_cant_be_none(cls, value: Optional[str]):
        if value is None:
            raise ValueError('Название проекта не может быть пустым.')
        return value

    @validator('description')
    def description_cant_be_none(cls, value: Optional[str]):
        if value is None:
            raise ValueError('Описание проекта не может быть пустым.')
        return value

    class Config:
        extra = Extra.forbid
