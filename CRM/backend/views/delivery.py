from decimal import Decimal
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.orders import DeliveryOrder, DeliveryOrderItem
from models.employees import Employee
from models.catalog import Product, Category


bp = Blueprint('delivery', __name__, url_prefix='/crm/delivery')


@bp.route('/')
@login_required
def home():
    new_orders = DeliveryOrder.query.filter_by(status='new').all()
    in_progress = DeliveryOrder.query.filter_by(status='in_progress').all()
    done = DeliveryOrder.query.filter_by(status='done').all()
    cancelled = DeliveryOrder.query.filter_by(status='cancelled').all()
    return render_template('delivery/home.html', new_orders=new_orders, in_progress=in_progress, done=done, cancelled=cancelled)


@bp.route('/new')
@login_required
def new():
    categories = Category.query.all()
    products = Product.query.filter_by(active=True).all()
    return render_template('delivery/edit.html', order=None, categories=categories, products=products)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    o = DeliveryOrder(
        phone=request.form.get('phone'),
        customer_name=request.form.get('customer_name'),
        street=request.form.get('street'),
        house=request.form.get('house'),
        flat=request.form.get('flat'),
        entrance=request.form.get('entrance'),
        floor=request.form.get('floor'),
        comment=request.form.get('comment'),
        receive_method=request.form.get('receive_method') or 'delivery',
        planned_at=datetime.fromisoformat(request.form.get('planned_at')) if request.form.get('planned_at') else None,
        payment_type=request.form.get('payment_type') or 'cash',
    )
    db.session.add(o)
    db.session.commit()
    return redirect(url_for('delivery.edit', order_id=o.id))


@bp.route('/<int:order_id>')
@login_required
def edit(order_id: int):
    order = DeliveryOrder.query.get_or_404(order_id)
    categories = Category.query.all()
    products = Product.query.filter_by(active=True).all()
    status_options = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    couriers = Employee.query.filter_by(position='Курьер').order_by(Employee.full_name.asc()).all()
    receive_map = {
        'delivery': 'Доставка',
        'pickup': 'Самовывоз',
        'dinein': 'В зале',
    }
    pay_map = {
        'cash': 'Наличные',
        'card': 'Карта',
        'online': 'Онлайн',
    }
    return render_template(
        'delivery/edit.html',
        order=order,
        categories=categories,
        products=products,
        status_options=status_options,
        couriers=couriers,
        receive_map=receive_map,
        pay_map=pay_map,
    )


@bp.route('/<int:order_id>/add', methods=['POST'])
@login_required
def add_item(order_id: int):
    order = DeliveryOrder.query.get_or_404(order_id)
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('qty') or '1')
    product = Product.query.get_or_404(product_id)
    line_sum = Decimal(product.price) * qty
    item = DeliveryOrderItem(order_id=order.id, product_id=product.id, product_name=product.name, qty=qty, unit_price=product.price, sum=line_sum)
    order.total = (Decimal(order.total) + line_sum)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('delivery.edit', order_id=order.id))


@bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def set_status(order_id: int):
    order = DeliveryOrder.query.get_or_404(order_id)
    status = request.form.get('status')
    courier_id = request.form.get('courier_id')
    if status in ['new', 'in_progress', 'done', 'cancelled']:
        order.status = status
    # сохраняем курьера, если передан
    if courier_id is not None:
        order.courier_id = int(courier_id) if courier_id else None
    db.session.commit()
    return redirect(url_for('delivery.home'))


@bp.route('/<int:order_id>/courier', methods=['POST'])
@login_required
def set_courier(order_id: int):
    order = DeliveryOrder.query.get_or_404(order_id)
    courier_id = request.form.get('courier_id')
    order.courier_id = int(courier_id) if courier_id else None
    db.session.commit()
    return redirect(url_for('delivery.edit', order_id=order.id))

