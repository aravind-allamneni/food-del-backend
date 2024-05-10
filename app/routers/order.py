from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
import datetime

from .. import models
from .. import schemas
from .. import oauth2
from ..database import get_db
from . import user
from ..payment import create_razorpay_order, verify_razorpay_payment
from app import payment

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


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.OrderOut])
async def get_orders(
    db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_user)
):
    try:
        orders = (
            db.query(models.Order)
            .filter(
                models.Order.user_id == current_user.id, models.Order.payment == True
            )
            .order_by(desc(models.Order.created_at))
            .all()
        )
        if not orders:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return orders
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {error}",
        )


@router.post("/verify_payment", status_code=status.HTTP_201_CREATED)
async def verify_transaction(
    transaction: schemas.Transaction,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_user),
):
    paymentSucess = verify_razorpay_payment(
        transaction.razorpay_order_id,
        transaction.razorpay_payment_id,
        transaction.razorpay_signature,
    )
    if not paymentSucess:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Payment not successfull try again",
        )
    new_transaction = models.Transaction(
        razorpay_order_id=transaction.razorpay_order_id,
        razorpay_payment_id=transaction.razorpay_payment_id,
        razorpay_signature=transaction.razorpay_signature,
        payment_status=paymentSucess,
    )
    try:
        db.add(new_transaction)
        db.query(models.Order).filter(
            models.Order.rz_id == transaction.razorpay_order_id
        ).update({"payment": True})
        db.commit()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment status: {paymentSucess} Veiify payment with bank.",
        )
