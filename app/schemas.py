from re import S
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Annotated, Optional


class MenuItem(BaseModel):
    name: str
    description: str
    category: str
    image: str
    price: float
    available: bool = True


class MenuItemOut(MenuItem):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MenuCategory(BaseModel):
    name: str
    image: str


class MenuCategoryOut(MenuCategory):
    id: int
    created_at: datetime


class Admin(BaseModel):
    email: EmailStr


class AdminIn(Admin):
    password: str


class AdminLogin(Admin):
    password: str


class AdminOut(Admin):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
