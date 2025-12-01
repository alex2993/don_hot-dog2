from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.orders import Table, Order, OrderItem, Payment
from models.catalog import Product


bp = Blueprint('orders', __name__, url_prefix='/crm/orders')


@bp.route('/')
@login_required
def index():
    tables = Table.query.order_by(Table.name.asc()).all()
    open_orders = Order.query.filter_by(status='open').all()
    status_map = {'open': 'Открыт', 'paid': 'Оплачен', 'cancelled': 'Отменён'}
    return render_template('orders/index.html', tables=tables, orders=open_orders, status_map=status_map)


@bp.route('/open', methods=['POST'])
@login_required
def open_order():
    table_id = request.form.get('table_id')
    order = Order(table_id=table_id)
    db.session.add(order)
    db.session.commit()
    flash('Открыт новый заказ', 'success')
    return redirect(url_for('orders.view', order_id=order.id))


@bp.route('/tables/create', methods=['POST'])
@login_required
def tables_create():
    name = request.form.get('name')
    if not name:
        flash('Укажите имя стола', 'warning')
        return redirect(url_for('orders.index'))
    if Table.query.filter_by(name=name).first():
        flash('Стол с таким именем уже существует', 'warning')
        return redirect(url_for('orders.index'))
    db.session.add(Table(name=name))
    db.session.commit()
    flash('Стол добавлен', 'success')
    return redirect(url_for('orders.index'))


@bp.route('/tables/delete/<int:table_id>', methods=['POST'])
@login_required
def tables_delete(table_id: int):
    t = Table.query.get_or_404(table_id)
    has_orders = Order.query.filter_by(table_id=t.id, status='open').first()
    if has_orders:
        flash('Нельзя удалить стол с открытыми заказами', 'warning')
        return redirect(url_for('orders.index'))
    db.session.delete(t)
    db.session.commit()
    flash('Стол удален', 'success')
    return redirect(url_for('orders.index'))


@bp.route('/<int:order_id>')
@login_required
def view(order_id: int):
    order = Order.query.get_or_404(order_id)
    products = Product.query.filter_by(active=True).all()
    return render_template('orders/view.html', order=order, products=products)


@bp.route('/<int:order_id>/add', methods=['POST'])
@login_required
def add_item(order_id: int):
    order = Order.query.get_or_404(order_id)
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('qty') or '1')
    product = Product.query.get_or_404(product_id)
    line_sum = Decimal(product.price) * qty
    item = OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, qty=qty, unit_price=product.price, sum=line_sum)
    order.total = (Decimal(order.total) + line_sum)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('orders.view', order_id=order.id))


@bp.route('/<int:order_id>/pay', methods=['POST'])
@login_required
def pay(order_id: int):
    order = Order.query.get_or_404(order_id)
    amount = order.total
    payment = Payment(order_id=order.id, amount=amount, method=request.form.get('method', 'cash'))
    order.status = 'paid'
    db.session.add(payment)
    db.session.commit()
    flash('Заказ оплачен', 'success')
    return redirect(url_for('orders.index'))


