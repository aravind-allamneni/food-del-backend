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
