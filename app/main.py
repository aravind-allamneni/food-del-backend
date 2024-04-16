from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import menuitem

from . import models
from .database import engine
from .routers import menuitem
from .routers import menucategory
from .routers import admin
from .routers import auth

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "Hello World! - from food-del-backend"}
