from sqlalchemy import ARRAY, JSON, Column, Float, Integer, String, Boolean, null
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    phone_number = Column(String, nullable=False)
    cart = Column(JSON)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.email})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, nullable=False)
    items = Column(ARRAY(JSON), nullable=False)
    amount = Column(Float, nullable=False)
    address = Column(JSON, nullable=False)
    status = Column(String, nullable=False, server_default="Processing")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    payment = Column(Boolean, server_default=text("False"))
    rz_id = Column(String, nullable=False, server_default="_")
