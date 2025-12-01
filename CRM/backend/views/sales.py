from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.orders import Table, Order, OrderItem, Payment
from models.employees import Employee
from models.catalog import Product, Category


bp = Blueprint('sales', __name__, url_prefix='/crm/sales')


@bp.route('/')
@login_required
def home():
    categories = Category.query.all()
    products = Product.query.filter_by(active=True).all()
    open_orders = Order.query.filter_by(status='open').all()
    staff = Employee.query.filter(Employee.position.in_(['Официант','Бармен'])).order_by(Employee.full_name.asc()).all()
    return render_template('sales/home.html', categories=categories, products=products, open_orders=open_orders, staff=staff)


@bp.route('/order/new', methods=['POST'])
@login_required
def order_new():
    table_id = request.form.get('table_id') or None
    guest_count = int(request.form.get('guest_count') or '1')
    waiter = request.form.get('waiter') or None
    order = Order(table_id=table_id, guest_count=guest_count, waiter=waiter)
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('sales.order_view', order_id=order.id))


@bp.route('/order/<int:order_id>')
@login_required
def order_view(order_id: int):
    categories = Category.query.all()
    products = Product.query.filter_by(active=True).all()
    order = Order.query.get_or_404(order_id)
    return render_template('sales/order.html', order=order, categories=categories, products=products)


@bp.route('/order/<int:order_id>/add', methods=['POST'])
@login_required
def order_add(order_id: int):
    order = Order.query.get_or_404(order_id)
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('qty') or '1')
    product = Product.query.get_or_404(product_id)
    line_sum = Decimal(product.price) * qty
    item = OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, qty=qty, unit_price=product.price, sum=line_sum)
    order.total = (Decimal(order.total) + line_sum)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('sales.order_view', order_id=order.id))


@bp.route('/order/<int:order_id>/qty', methods=['POST'])
@login_required
def order_qty(order_id: int):
    item_id = int(request.form.get('item_id'))
    delta = int(request.form.get('delta'))
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    new_qty = max(1, item.qty + delta)
    diff = (new_qty - item.qty) * item.unit_price
    item.qty = new_qty
    item.sum = item.unit_price * new_qty
    order.total = (Decimal(order.total) + Decimal(diff))
    db.session.commit()
    return redirect(url_for('sales.order_view', order_id=order.id))


@bp.route('/order/<int:order_id>/remove', methods=['POST'])
@login_required
def order_remove(order_id: int):
    item_id = int(request.form.get('item_id'))
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)
    order.total = (Decimal(order.total) - Decimal(item.sum))
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('sales.order_view', order_id=order.id))


@bp.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
def order_pay(order_id: int):
    order = Order.query.get_or_404(order_id)
    method = request.form.get('method', 'cash')
    payment = Payment(order_id=order.id, amount=order.total, method=method)
    order.status = 'paid'
    db.session.add(payment)
    db.session.commit()
    flash('Чек закрыт', 'success')
    return redirect(url_for('sales.home'))

