import re

from fastapi import Body, Query
from pydantic import BaseModel, validator


class UserRegisterFake(BaseModel):
    date: str

    @classmethod
    def as_params(cls,
                  date: str = Body(..., title="日期", description="日期")):
        return cls(date=date)

    @validator('date')
    def date_regex_or_empty(cls, v):
        reg = r"^202[0-9]{1}[0-9]{2}[0-9]{2}$"
        if not re.findall(reg, v):
            raise ValueError('开始时间格式错误')
        return v


class UserSignRequest(BaseModel):
    date: str
    user_id: int

    @classmethod
    def as_params(cls,
                  date: str = Query(..., title="日期（日）", description="日期（日）"),
                  user_id: int = Query(..., title="用户", description="用户")):
        return cls(date=date, user_id=user_id)

    @validator('date')
    def date_regex_or_empty(cls, v):
        reg = r"^202[0-9]{1}[0-9]{2}[0-9]{2}$"
        if not re.findall(reg, v):
            raise ValueError('开始时间格式错误')
        return v


class UserSignForMonthRequest(BaseModel):
    date: str
    user_id: int

    @classmethod
    def as_params(cls,
                  date: str = Query(..., title="日期(月)", description="日期（月）"),
                  user_id: int = Query(..., title="用户", description="用户")):
        return cls(date=date, user_id=user_id)

    @validator('date')
    def date_regex_or_empty(cls, v):
        reg = r"^202[0-9]{1}[0-9]{2}$"
        if not re.findall(reg, v):
            raise ValueError('开始时间格式错误')
        return v
