from http.client import HTTP_PORT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models
from .. import utils
from .. import oauth2

from ..schemas import Token
from ..database import get_db

router = APIRouter(tags=["Authentication"])


@router.post("/admin", response_model=Token)
async def login_admin(
    admin_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    admin = (
        db.query(models.Admin)
        .filter(models.Admin.email == admin_credentials.username)
        .first()
    )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    if not utils.verify(admin_credentials.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": admin.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/user", response_model=Token)
async def login_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # check if a user exists with the given credentials and raise forbidded if not
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    # verify given credentials and revert with forbidden error
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
