from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from .. import utils

from ..database import get_db

router = APIRouter(tags=["Admins"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.AdminOut,
    include_in_schema=False,
)
async def create_admin(admin: schemas.AdminIn, db: Session = Depends(get_db)):
    hashed_password = utils.hash(admin.password)
    admin.password = hashed_password
    new_admin = models.Admin(**admin.model_dump())
    db.add(new_admin)
    try:
        db.commit()
        db.refresh(new_admin)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"admin could not be created"
        )
    return new_admin
