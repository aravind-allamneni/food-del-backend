from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import menuitem, user

from . import models
from .database import engine
from .routers import menuitem
from .routers import menucategory
from .routers import admin
from .routers import auth
from .routers import order

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app = FastAPI()

app.mount(
    "/images/menuitems/",
    StaticFiles(directory="./images/menuitems/"),
    name="images",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menuitem.router, prefix="/menuitems")
app.include_router(menucategory.router, prefix="/menucategories")
app.include_router(admin.router, prefix="/admin")
app.include_router(auth.router, prefix="/login")
app.include_router(user.router, prefix="/users")
app.include_router(order.router, prefix="/orders")


@app.get("/")
async def root():
    return {"message": "Hello World! - from food-del-backend"}
