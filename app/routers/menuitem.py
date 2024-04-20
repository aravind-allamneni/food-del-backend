from typing import Union
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
    UploadFile,
    File,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import shutil
import os

from ..config import settings

from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db

UPLOAD_FOLDER = settings.upload_folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(tags=["MenuItems"])


@router.get("/", response_model=list[schemas.MenuItemOut])
async def get_all_menu_items(
    search: Union[str, None] = "",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    menuitems = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.name.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    if not menuitems:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return menuitems


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MenuItemOut,
    # dependencies=[Depends(oauth2.get_admin)],
)
async def create_menuitem(
    menuitem: schemas.MenuItem,
    db: Session = Depends(get_db),
):
    new_menuitem = models.MenuItem(**menuitem.model_dump())
    db.add(new_menuitem)
    try:
        db.commit()
        db.refresh(new_menuitem)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Menu item not created"
        )
    return new_menuitem


@router.get("/{id}", response_model=schemas.MenuItemOut)
async def get_one_menu_item(id: int, db: Session = Depends(get_db)):
    menuitem = db.query(models.MenuItem).filter(models.MenuItem.id == id).first()
    if not menuitem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no menu item with id: {id} found",
        )
    return menuitem


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(oauth2.get_admin)],
)
async def delete_menu_item(
    id: int,
    db: Session = Depends(get_db),
):
    menuitem_query = db.query(models.MenuItem).filter(models.MenuItem.id == id)
    menuitem = menuitem_query.first()
    if not menuitem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"menu item with id: {id} not found",
        )
    menuitem_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{id}",
    response_model=schemas.MenuItemOut,
    # dependencies=[Depends(oauth2.get_admin)],
)
async def update_menu_item(
    id: int,
    menuitem: schemas.MenuItem,
    db: Session = Depends(get_db),
):
    menu_item_query = db.query(models.MenuItem).filter(models.MenuItem.id == id)
    existing_menuitem = menu_item_query.first()
    if not existing_menuitem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"no item with id: {id} found"
        )
    menu_item_query.update(menuitem.model_dump(), synchronize_session=False)
    db.commit()
    updated_menu_item = menu_item_query.first()
    return updated_menu_item


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(os.path.abspath(os.path.join(UPLOAD_FOLDER, file.filename)))
        return JSONResponse(
            content={
                "message": "File uploaded successfully",
                "file_url": f"{UPLOAD_FOLDER}/{file.filename}",
            }
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(error)}"
        )
