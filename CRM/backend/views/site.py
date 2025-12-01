from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple

from flask import (
    Blueprint,
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    jsonify,
)
from flask_login import current_user, login_required
import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from models.user import User

from app import db
from models.catalog import Product, Category
from models.orders import DeliveryOrder, DeliveryOrderItem
from models.crm import Customer, JobApplication
from models.reviews import Review


bp = Blueprint('site', __name__)


def _get_cart() -> Dict[str, int]:
    cart = session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    return {str(k): int(v) for k, v in cart.items() if int(v) > 0}


def _save_cart(cart: Dict[str, int]) -> None:
    session['cart'] = cart
    session.modified = True


def _cart_items(cart: Dict[str, int]) -> Tuple[List[Dict[str, object]], Decimal]:
    if not cart:
        return [], Decimal('0')
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    products_by_id = {p.id: p for p in products}
    items: List[Dict[str, object]] = []
    total = Decimal('0')
    for pid_str, qty in cart.items():
        product = products_by_id.get(int(pid_str))
        if not product:
            continue
        price = Decimal(product.price or 0)
        line_total = price * qty
        total += line_total
        items.append(
            {
                'product': product,
                'quantity': qty,
                'price': price,
                'line_total': line_total,
            }
        )
    return items, total


@bp.context_processor
def inject_cart_summary():
    cart = _get_cart()
    quantity = sum(cart.values())
    return {'site_cart_count': quantity}


@bp.route('/')
def home():
    featured_products = (
        Product.query.filter_by(active=True)
        .order_by(Product.price.desc(), Product.name.asc())
        .limit(6)
        .all()
    )
    categories = Category.query.order_by(Category.name.asc()).limit(6).all()
    return render_template(
        'site/home.html',
        featured_products=featured_products,
        categories=categories,
    )


@bp.route('/menu/')
def menu():
    categories = Category.query.order_by(Category.name.asc()).all()
    products = Product.query.filter_by(active=True).order_by(Product.name.asc()).all()
    products_by_category: Dict[int | None, List[Product]] = {}
    for product in products:
        products_by_category.setdefault(product.category_id, []).append(product)
    return render_template(
        'site/menu.html',
        categories=categories,
        products_by_category=products_by_category,
    )


@bp.route('/basket/')
def basket():
    cart = _get_cart()
    items, total = _cart_items(cart)
    return render_template('site/basket.html', items=items, total=total)


@bp.route('/basket/add', methods=['POST'])
def basket_add():
    product_id = request.form.get('product_id')
    qty = int(request.form.get('qty') or 1)
    if not product_id:
        flash('Не удалось определить товар', 'warning')
        return redirect(request.referrer or url_for('site.menu'))
    cart = _get_cart()
    cart[product_id] = cart.get(product_id, 0) + max(1, qty)
    _save_cart(cart)
    flash('Товар добавлен в корзину', 'success')
    return redirect(request.referrer or url_for('site.basket'))


@bp.route('/basket/update', methods=['POST'])
def basket_update():
    cart = _get_cart()
    for product_id, qty in request.form.items():
        if not product_id.startswith('qty_'):
            continue
        pid = product_id.split('_', 1)[1]
        try:
            cart[pid] = max(0, int(qty))
            if cart[pid] == 0:
                cart.pop(pid, None)
        except ValueError:
            continue
    _save_cart(cart)
    flash('Корзина обновлена', 'success')
    return redirect(url_for('site.basket'))


@bp.route('/basket/remove', methods=['POST'])
def basket_remove():
    product_id = request.form.get('product_id')
    cart = _get_cart()
    if product_id in cart:
        cart.pop(product_id)
        _save_cart(cart)
        flash('Товар удалён из корзины', 'info')
    return redirect(url_for('site.basket'))


@bp.route('/basket/clear', methods=['POST'])
def basket_clear():
    _save_cart({})
    flash('Корзина очищена', 'info')
    return redirect(url_for('site.basket'))


@bp.route('/basket/checkout', methods=['POST'])
def basket_checkout():
    cart = _get_cart()
    items, total = _cart_items(cart)
    if not items:
        flash('В корзине нет товаров', 'warning')
        return redirect(url_for('site.basket'))

    customer_name = request.form.get('customer_name') or (current_user.full_name if current_user.is_authenticated else None)
    contact_email = (request.form.get('phone') or '').strip()
    if not contact_email and current_user.is_authenticated:
        contact_email = (current_user.email or '').strip()
    contact_phone = (request.form.get('contact_phone') or '').strip()
    if contact_phone:
        digits = ''.join(ch for ch in contact_phone if ch.isdigit())
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7') and len(digits) == 10:
            digits = '7' + digits
        if digits.startswith('7'):
            contact_phone = '+' + digits
        else:
            contact_phone = '+' + digits if digits else ''
    street = request.form.get('street')
    house = request.form.get('house')
    flat = request.form.get('flat')
    comment = request.form.get('comment')

    if not customer_name or not contact_phone:
        flash('Укажите имя и контактный телефон', 'warning')
        return redirect(url_for('site.basket'))

    order = DeliveryOrder(
        status='new',
        source='site',
        customer_name=customer_name,
        phone=contact_phone,
        street=street,
        house=house,
        flat=flat,
        comment=comment,
        receive_method='delivery',
        payment_type=request.form.get('payment_type') or 'cash',
        total=total,
    )
    if current_user.is_authenticated:
        order.user_id = current_user.id
    if contact_email:
        email_note = f"E-mail: {contact_email}"
        order.comment = f"{order.comment}\n{email_note}" if order.comment else email_note
    order.phone = contact_phone
    db.session.add(order)
    db.session.flush()

    for item in items:
        product: Product = item['product']
        db.session.add(
            DeliveryOrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                qty=item['quantity'],
                unit_price=item['price'],
                sum=item['line_total'],
            )
        )

    customer = Customer.query.filter_by(phone=contact_phone).first()
    if not customer:
        customer = Customer(phone=contact_phone, name=customer_name)
        db.session.add(customer)
    customer.points = (customer.points or 0) + int(total)

    db.session.commit()
    _save_cart({})
    flash('Спасибо! Заказ принят, мы свяжемся с вами.', 'success')
    return redirect(url_for('site.profile') if current_user.is_authenticated else url_for('site.home'))


@bp.route('/policy/')
def policy():
    return render_template('site/policy.html')


def _parse_rating(raw: str | None) -> int:
    try:
        value = int(raw or 0)
    except (TypeError, ValueError):
        raise ValueError('Оценка должна быть числом')
    if value < 0 or value > 10:
        raise ValueError('Оценка должна быть в диапазоне 0-10')
    return value


@bp.route('/reviews/', methods=['GET', 'POST'])
def reviews():
    form_data = {
        'service_rating': request.form.get('service_rating', '5'),
        'product_rating': request.form.get('product_rating', '5'),
        'ambience_rating': request.form.get('ambience_rating', '5'),
        'recommend_rating': request.form.get('recommend_rating', '5'),
        'comment': request.form.get('comment', ''),
        'location': request.form.get('location', ''),
    }

    if request.method == 'POST':
        try:
            service_rating = _parse_rating(request.form.get('service_rating'))
            product_rating = _parse_rating(request.form.get('product_rating'))
            ambience_rating = _parse_rating(request.form.get('ambience_rating'))
            recommend_rating = _parse_rating(request.form.get('recommend_rating'))
        except ValueError as exc:
            flash(str(exc), 'warning')
        else:
            review = Review(
                user_id=current_user.id if current_user.is_authenticated else None,
                author_name=(current_user.full_name or current_user.email) if current_user.is_authenticated else None,
                service_rating=service_rating,
                product_rating=product_rating,
                ambience_rating=ambience_rating,
                recommend_rating=recommend_rating,
                comment=(request.form.get('comment') or '').strip() or None,
                location=(request.form.get('location') or '').strip() or None,
            )
            db.session.add(review)
            db.session.commit()
            flash('Спасибо за отзыв! Он поможет нам стать лучше.', 'success')
            return redirect(url_for('site.reviews') + '#reviews-list')

    reviews_list = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('site/reviews.html', reviews=reviews_list, form_data=form_data)


@bp.route('/api/products/<int:product_id>/')
def product_details(product_id: int):
    product = Product.query.filter_by(id=product_id, active=True).first_or_404()
    image_url = product.image_url or ''
    if image_url and not image_url.startswith(('http://', 'https://')):
        image_url = url_for('static', filename=image_url)
    data = {
        'id': product.id,
        'name': product.name,
        'price': float(product.price or 0),
        'description': product.description or '',
        'image_url': image_url,
        'portion_grams': product.portion_grams,
        'protein_100g': float(product.protein_100g) if product.protein_100g is not None else None,
        'fat_100g': float(product.fat_100g) if product.fat_100g is not None else None,
        'carb_100g': float(product.carb_100g) if product.carb_100g is not None else None,
        'kcal_100g': product.kcal_100g,
        'category': product.category.name if product.category else None,
    }
    return jsonify(data)


@bp.route('/work/', methods=['GET', 'POST'])
def work():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        desired_position = (request.form.get('professia') or '').strip()
        city = (request.form.get('city') or '').strip()
        phone = (request.form.get('number') or '').strip()
        email = (request.form.get('email') or '').strip()

        if not name or not phone or not email:
            flash('Заполните имя, телефон и e-mail.', 'warning')
        else:
            application = JobApplication(
                name=name[:120],
                desired_position=desired_position[:120] or None,
                city=city[:120] or None,
                phone=contact_phone[:50] or None,
                email=email[:120] or None,
            )
            db.session.add(application)
            db.session.commit()
            flash('Спасибо! Мы свяжемся с вами.', 'success')
            return redirect(url_for('site.work'))

    return render_template('site/work.html')


@bp.route('/profile/')
@login_required
def profile():
    orders = (
        DeliveryOrder.query.filter_by(user_id=current_user.id)
        .order_by(DeliveryOrder.created_at.desc())
        .all()
    )
    customer = None
    if orders:
        first_phone = next((order.phone for order in orders if order.phone), None)
        if first_phone:
            customer = Customer.query.filter_by(phone=first_phone).first()
    return render_template('site/profile.html', orders=orders, customer=customer)


@bp.route('/profile/update-full-name', methods=['POST'])
@login_required
def update_full_name():
    full_name = (request.form.get('full_name') or '').strip()
    current_user.full_name = full_name if full_name else None
    db.session.commit()
    flash('ФИО успешно изменено', 'success')
    return redirect(url_for('site.profile'))


@bp.route('/profile/update-email', methods=['POST'])
@login_required
def update_email():
    new_email = (request.form.get('new_email') or '').strip().lower()
    if not new_email:
        flash('Email не может быть пустым', 'warning')
        return redirect(url_for('site.profile'))
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user and existing_user.id != current_user.id:
        flash('Этот email уже используется другим пользователем', 'warning')
        return redirect(url_for('site.profile'))
    current_user.email = new_email
    db.session.commit()
    flash('Email успешно изменён', 'success')
    return redirect(url_for('site.profile'))


@bp.route('/profile/update-password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password') or ''
    new_password = request.form.get('new_password') or ''
    confirm_password = request.form.get('confirm_password') or ''
    if not current_password or not new_password or not confirm_password:
        flash('Заполните все поля', 'warning')
        return redirect(url_for('site.profile'))
    if not current_user.check_password(current_password):
        flash('Неверный текущий пароль', 'warning')
        return redirect(url_for('site.profile'))
    if new_password != confirm_password:
        flash('Новый пароль и подтверждение не совпадают', 'warning')
        return redirect(url_for('site.profile'))
    if len(new_password) < 6:
        flash('Пароль должен содержать минимум 6 символов', 'warning')
        return redirect(url_for('site.profile'))
    current_user.set_password(new_password)
    db.session.commit()
    flash('Пароль успешно изменён', 'success')
    return redirect(url_for('site.profile'))


@bp.route('/profile/update-avatar', methods=['POST'])
@login_required
def update_avatar():
    avatar = request.files.get('avatar')
    if avatar and avatar.filename:
        ext = os.path.splitext(avatar.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            flash('Неподдерживаемый формат изображения. Используйте JPG, PNG, GIF или WEBP', 'warning')
            return redirect(url_for('site.profile'))

        if current_user.avatar_url:
            try:
                old_path = current_user.avatar_url.replace('/static/', '')
                full_old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', old_path)
                if os.path.exists(full_old_path):
                    os.remove(full_old_path)
            except Exception:
                pass
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'avatars')
        os.makedirs(uploads_dir, exist_ok=True)
        filename = secure_filename(f"{uuid4().hex}{ext}")
        avatar.save(os.path.join(uploads_dir, filename))
        current_user.avatar_url = f"/static/uploads/avatars/{filename}"
        db.session.commit()
        flash('Аватар успешно обновлен', 'success')
    else:
        flash('Файл не выбран', 'warning')
    return redirect(url_for('site.profile'))


@bp.route('/profile/delete-avatar', methods=['POST'])
@login_required
def delete_avatar():
    if current_user.avatar_url:
        try:
            avatar_path = current_user.avatar_url.replace('/static/', '')
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', avatar_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception:
            pass
    current_user.avatar_url = None
    db.session.commit()
    flash('Аватар удален', 'success')
    return redirect(url_for('site.profile'))


@bp.route('/api/order/<int:order_id>/details/')
@login_required
def order_details(order_id):
    order = DeliveryOrder.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    items = []
    for item in order.items:
        items.append({
            'product_name': item.product_name,
            'qty': int(item.qty or 0),
            'unit_price': float(item.unit_price or 0),
            'sum': float(item.sum or 0),
        })
    status_map = {
        'new': 'Новый',
        'in_progress': 'В процессе',
        'done': 'Выполнен',
        'cancelled': 'Отменён',
    }
    return jsonify({
        'id': order.id,
        'created_at': order.created_at.strftime('%d.%m.%Y %H:%M') if order.created_at else '—',
        'status': status_map.get(order.status, order.status),
        'comment': order.comment or '—',
        'total': float(order.total or 0),
        'items': items,
    })

