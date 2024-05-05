from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any, Optional, Dict


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


class User(BaseModel):
    email: EmailStr


class UserIn(User):
    password: str
    name: str
    phone_number: str
    cart: Dict[str, int] = {}


class UserUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    cart: Dict[str, int] | None


class UserLogin(User):
    password: str


class UserOut(User):
    id: int
    name: str
    created_at: datetime
    phone_number: str
    cart: Dict[str, int]


class OrderIn(BaseModel):
    items: list[dict[str, Any]]
    amount: float
    address: dict


class OrderOut(OrderIn):
    id: int
    user_id: int
    status: str
    payment: bool
    created_at: datetime
    rz_id: str


class Transaction(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
