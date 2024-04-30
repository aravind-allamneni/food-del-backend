from copyreg import constructor
from urllib import response
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db
from . import user

router = APIRouter(tags=["Orders"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.OrderOut)
async def place_order(
    order_details: schemas.OrderIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    new_order = models.Order(
        user_id=current_user.id,
        items=order_details.items,
        amount=order_details.amount,
        address=order_details.address,
    )
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        response = await user.add_to_cart(
            id=current_user.id, cart={}, db=db, current_user=current_user
        )
        print(response)
        return new_order
    except Exception as error:
        print(f"Error Order cound not be placed: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {error}",
        )
