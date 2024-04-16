from sqlalchemy import Column, Float, Integer, String, Boolean, null
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base


class MenuItem(Base):
    __tablename__ = "menuitems"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    image = Column(String)
    price = Column(Float, nullable=False)
    available = Column(Boolean, nullable=False, server_default=text("True"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class MenuCategory(Base):
    __tablename__ = "menucategories"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    image = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    phone_number = Column(String)
