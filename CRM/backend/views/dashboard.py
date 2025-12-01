from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app import db
from models.orders import DeliveryOrder, Order, Payment

bp = Blueprint('dashboard', __name__, url_prefix='/crm')


def _calc_change(current: float, previous: float) -> Optional[float]:
    if previous in (None, 0):
        return None
    return round(((current - previous) / previous) * 100, 1)


@bp.route('/')
@login_required
def index():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    orders_today = (
        db.session.query(func.count(Order.id))
        .filter(func.date(Order.created_at) == today)
        .scalar()
    )
    orders_yesterday = (
        db.session.query(func.count(Order.id))
        .filter(func.date(Order.created_at) == yesterday)
        .scalar()
    )
    revenue_today_raw = (
        db.session.query(func.coalesce(func.sum(Order.total), 0))
        .filter(
            func.date(Order.created_at) == today,
            Order.status == 'paid',
        )
        .scalar()
    )
    revenue_yesterday_raw = (
        db.session.query(func.coalesce(func.sum(Order.total), 0))
        .filter(
            func.date(Order.created_at) == yesterday,
            Order.status == 'paid',
        )
        .scalar()
    )
    revenue_today = float(revenue_today_raw or 0)
    revenue_yesterday = float(revenue_yesterday_raw or 0)
    open_orders = Order.query.filter_by(status='open').count()
    pending_delivery = DeliveryOrder.query.filter(
        DeliveryOrder.status.notin_(['done', 'cancelled'])
    ).count()

    latest_orders = (
        Order.query.order_by(Order.created_at.desc()).limit(5).all()
    )
    latest_deliveries = (
        DeliveryOrder.query.order_by(DeliveryOrder.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'dashboard/index.html',
        orders_today=orders_today,
        orders_change=_calc_change(orders_today, orders_yesterday),
        revenue_today=revenue_today,
        revenue_change=_calc_change(revenue_today, revenue_yesterday),
        open_orders=open_orders,
        pending_delivery=pending_delivery,
        latest_orders=latest_orders,
        latest_deliveries=latest_deliveries,
    )
