from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db
from . import user
from ..payment import create_razorpay_order

router = APIRouter(tags=["Orders"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.OrderOut)
async def place_order(
    order_details: schemas.OrderIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    razorpay_order = create_razorpay_order(
        order_details.amount,
        "INR",
        f"{current_user.id}_{datetime.datetime.now()}",
        {"notes:": "Notes"},
    )
    new_order = models.Order(
        user_id=current_user.id,
        items=order_details.items,
        amount=order_details.amount,
        address=order_details.address,
        rz_id=razorpay_order["id"],
    )
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        response = await user.add_to_cart(
            id=current_user.id, cart={}, db=db, current_user=current_user
        )
        return new_order
    except Exception as error:
        print(f"Error Order cound not be placed: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {error}",
        )
