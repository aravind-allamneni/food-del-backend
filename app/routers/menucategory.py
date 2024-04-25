from email.policy import HTTP
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import oauth2
from .. import models
from .. import schemas
from ..database import get_db


router = APIRouter(tags=["MenuCategories"])


@router.get("/", response_model=list[schemas.MenuCategoryOut])
async def get_all_menu_categories(db: Session = Depends(get_db)):
    menucategories = db.query(models.MenuCategory).all()
    if not menucategories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return menucategories


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MenuCategoryOut,
    dependencies=[Depends(oauth2.get_admin)],
)
async def create_menu_category(
    menucategory: schemas.MenuCategory,
    db: Session = Depends(get_db),
):
    new_menucategory = models.MenuCategory(**menucategory.model_dump())
    db.add(new_menucategory)
    try:
        db.commit()
        db.refresh(new_menucategory)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Menu category not created"
        )
    return new_menucategory


@router.get("/{id}", response_model=schemas.MenuCategoryOut)
async def get_one_menu_category(id: int, db: Session = Depends(get_db)):
    menucategory = (
        db.query(models.MenuCategory).filter(models.MenuCategory.id == id).first()
    )
    if not menucategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no menu category with id: {id} found",
        )
    return menucategory


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(oauth2.get_admin)],
)
async def delete_menu_category(
    id: int,
    db: Session = Depends(get_db),
):
    menucategory_query = db.query(models.MenuCategory).filter(
        models.MenuCategory.id == id
    )
    menucategory = menucategory_query.first()
    if not menucategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"menu category with id: {id} not found",
        )
    menucategory_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{id}",
    response_model=schemas.MenuCategoryOut,
    dependencies=[Depends(oauth2.get_admin)],
)
async def update_menu_category(
    id: int,
    menucategory: schemas.MenuCategory,
    db: Session = Depends(get_db),
):
    menu_category_query = db.query(models.MenuCategory).filter(
        models.MenuCategory.id == id
    )
    existing_menu_category = menu_category_query.first()
    if not existing_menu_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no menu category with id: {id} found",
        )
    menu_category_query.update(menucategory.model_dump(), synchronize_session=False)
    db.commit()
    updated_menu_category = menu_category_query.first()
    return updated_menu_category
