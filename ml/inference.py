from app.database_models import Order

from sqlalchemy import func
from datetime import datetime, timedelta, UTC
import pandas as pd

from fastapi import Request

def get_avg_daily_sales(db, product_id: int):
    cutoff_date = datetime.now(tz=UTC) - timedelta(days=30)

    result = (
        db.query(
            func.coalesce(func.sum(Order.quantity), 0) / 30.0
        )
        .filter(
            Order.product_id == product_id,
            Order.created_at >= cutoff_date
        )
        .scalar()
    )

    return result or 0.0

def build_features(product, db):
    avg_daily_sales = get_avg_daily_sales(db, product.id)
    days_to_restock = 5
    
    new_features = [[
        product.quantity,
        avg_daily_sales,
        days_to_restock,
        product.price
    ]]

    return pd.DataFrame(new_features, columns=["quantity", "avg_daily_sales", "days_to_restock", "price"])

def predict_low_stock(features: list, request: Request):
    model = request.app.state.model
    prediction = model.predict(features)

    return prediction

