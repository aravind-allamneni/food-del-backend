import email
from fastapi import APIRouter, Depends, HTTPException, status

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
    user.cart = {}
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

