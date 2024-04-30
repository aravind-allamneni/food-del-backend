from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from .. import utils
from .. import oauth2
from ..database import get_db

router = APIRouter(tags=["Users"])


@router.get(
    "/",
    response_model=list[schemas.UserOut],
    dependencies=[Depends(oauth2.get_admin)],
)
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users Found"
        )
    return users


@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserIn, db: Session = Depends(get_db)):
    # check if email already exists and returh with conflict if it does
    try:
        userExists = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not created"
        )
    if userExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already exists"
        )
    # check if teh password length > 8 chars revert with error if not
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_411_LENGTH_REQUIRED,
            detail="Password length insufficient",
        )
    # build the User object with hashed password and empty cart
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    # user.cart = {}
    new_user = models.User(**user.model_dump())
    # push the new user to db
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not created"
        )
    # return newly created user back to caller
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not authorised to access other users data",
        )
    try:
        user = db.query(models.User).filter(models.User.id == id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} not found",
            )
        return user
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {error}",
        )


@router.put("/{id}", response_model=schemas.UserOut)
async def update_user(
    id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not allowed to modify others users data",
        )
    user_query = db.query(models.User).filter(models.User.id == id)
    try:
        existing_user = user_query.first()
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"no user with id: {id} found",
            )
        user_updates = {}
        if user.name:
            user_updates.update({"name", user.name})
        if user.phone_number:
            user_updates.update({"phone_number", user.phone_number})
        if user.cart:
            user_updates.update({"cart": user.cart})
        user_query.update(user_updates, synchronize_session=False)
        db.commit()
        updated_user = user_query.first()
        return updated_user
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(error)}",
        )


@router.get("/{id}/cart", response_model=dict)
async def get_user_cart(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to access cart",
        )
    # print(current_user.cart)
    return current_user.cart


@router.post("/{id}/cart", response_model=dict)
async def add_to_cart(
    id: int,
    cart: Dict[str, int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not allowed to modify others users data",
        )
    user_query = db.query(models.User).filter(models.User.id == id)
    try:
        existing_user = user_query.first()
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"no user with id: {id} found",
            )
        user_updates = {}
        user_updates.update({"cart": cart})
        user_query.update(user_updates, synchronize_session=False)
        db.commit()
        updated_user = user_query.first()
        return updated_user.cart
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(error)}",
        )
