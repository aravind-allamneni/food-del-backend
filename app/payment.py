from fastapi.exceptions import ValidationException
import razorpay
from .config import settings

client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_razorpay_order(amount: int, currency: str, receipt: str, notes: str):
    data = {
        "amount": amount * 100,
        "currency": currency,
        "receipt": receipt,
        "notes": notes,
    }
    try:
        order_data = client.order.create(data=data)
        return order_data
    except Exception as error:
        raise error


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    try:
        return client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except Exception as error:
        raise ValidationException(error)
