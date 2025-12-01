import os
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from app import db
from models.catalog import Category, Product


bp = Blueprint('catalog', __name__, url_prefix='/crm/catalog')


def _parse_optional_decimal(raw_value: str, label: str, errors: List[str]) -> Optional[Decimal]:
    value = (raw_value or '').strip()
    if not value:
        return None
    try:
        return Decimal(value.replace(',', '.'))
    except (InvalidOperation, AttributeError):
        errors.append(f'Некорректное значение поля «{label}».')
        return None


def _parse_optional_int(raw_value: str, label: str, errors: List[str]) -> Optional[int]:
    value = (raw_value or '').strip()
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        errors.append(f'Некорректное значение поля «{label}».')
        return None


def _extract_product_form(form) -> Tuple[Dict[str, object], List[str]]:
    errors: List[str] = []
    name = (form.get('name') or '').strip()
    if not name:
        errors.append('Укажите название блюда.')

    price_raw = (form.get('price') or '').strip()
    price = None
    if not price_raw:
        errors.append('Укажите цену за порцию.')
    else:
        try:
            price = Decimal(price_raw.replace(',', '.'))
        except InvalidOperation:
            errors.append('Некорректное значение цены.')

    description = (form.get('description') or '').strip()

    portion_grams = _parse_optional_int(form.get('portion_grams'), 'Вес порции', errors)
    protein_100g = _parse_optional_decimal(form.get('protein_100g'), 'Белки / 100 г', errors)
    fat_100g = _parse_optional_decimal(form.get('fat_100g'), 'Жиры / 100 г', errors)
    carb_100g = _parse_optional_decimal(form.get('carb_100g'), 'Углеводы / 100 г', errors)
    kcal_100g = _parse_optional_int(form.get('kcal_100g'), 'Ккал / 100 г', errors)

    category_id_raw = (form.get('category_id') or '').strip()
    category_id = None
    if category_id_raw:
        try:
            category_id = int(category_id_raw)
        except ValueError:
            errors.append('Некорректное значение категории.')

    data: Dict[str, object] = {
        'name': name,
        'price': price,
        'description': description or None,
        'portion_grams': portion_grams,
        'protein_100g': protein_100g,
        'fat_100g': fat_100g,
        'carb_100g': carb_100g,
        'kcal_100g': kcal_100g,
        'category_id': category_id,
    }
    return data, errors


def _product_to_form_data(product: Product) -> Dict[str, str]:
    def fmt_decimal(value, places: Optional[int] = None) -> str:
        if value is None:
            return ''
        if places is not None:
            return f'{value:.{places}f}'
        return format(value, 'f')

    return {
        'name': product.name or '',
        'price': fmt_decimal(product.price, 2) if product.price is not None else '',
        'description': product.description or '',
        'portion_grams': str(product.portion_grams) if product.portion_grams is not None else '',
        'protein_100g': fmt_decimal(product.protein_100g) if product.protein_100g is not None else '',
        'fat_100g': fmt_decimal(product.fat_100g) if product.fat_100g is not None else '',
        'carb_100g': fmt_decimal(product.carb_100g) if product.carb_100g is not None else '',
        'kcal_100g': str(product.kcal_100g) if product.kcal_100g is not None else '',
        'category_id': str(product.category_id) if product.category_id is not None else '',
    }


def _store_product_image(file_storage, previous_path: Optional[str] = None) -> Optional[str]:
    if not file_storage or not file_storage.filename:
        return previous_path

    filename = secure_filename(file_storage.filename)
    if not filename:
        return previous_path

    _, ext = os.path.splitext(filename)
    unique_name = f'{uuid4().hex}{ext.lower()}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'products')
    os.makedirs(upload_dir, exist_ok=True)

    target_path = os.path.join(upload_dir, unique_name)
    file_storage.save(target_path)

    if previous_path and not previous_path.startswith(('http://', 'https://')):
        old_path = os.path.join(current_app.static_folder, previous_path.replace('/', os.sep))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    relative_path = os.path.join('uploads', 'products', unique_name).replace('\\', '/')
    return relative_path


@bp.route('/')
@login_required
def list_products():
    view_mode = request.args.get('view', 'grid')
    if view_mode not in {'grid', 'list'}:
        view_mode = 'grid'

    selected_category_id = request.args.get('category', type=int)
    product_query = Product.query
    if selected_category_id is not None:
        product_query = product_query.filter(Product.category_id == selected_category_id)

    products = product_query.order_by(Product.name.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template(
        'catalog/products.html',
        products=products,
        categories=categories,
        view_mode=view_mode,
        selected_category_id=selected_category_id,
    )


@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    form_state: Dict[str, str] = {}
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        parent_id_raw = (request.form.get('parent_id') or '').strip()
        errors: List[str] = []
        parent_id: Optional[int] = None

        if not name:
            errors.append('Укажите название категории.')
        if parent_id_raw:
            try:
                parent_id = int(parent_id_raw)
                if not Category.query.get(parent_id):
                    errors.append('Выбранная родительская категория не найдена.')
            except ValueError:
                errors.append('Некорректное значение родительской категории.')

        if not errors:
            duplicate = (
                Category.query.filter(
                    func.lower(Category.name) == name.lower(),
                    Category.parent_id == parent_id,
                )
                .first()
            )
            if duplicate:
                errors.append('Категория с таким названием уже существует в этом разделе.')

        if errors:
            for error in errors:
                flash(error, 'warning')
            form_state = {'name': name, 'parent_id': parent_id_raw}
        else:
            category = Category(name=name, parent_id=parent_id)
            db.session.add(category)
            db.session.commit()
            flash('Категория добавлена', 'success')
            return redirect(url_for('catalog.manage_categories'))

    categories = Category.query.order_by(Category.name.asc()).all()
    counts = dict(
        db.session.query(Category.id, func.count(Product.id))
        .outerjoin(Product, Product.category_id == Category.id)
        .group_by(Category.id)
        .all()
    )
    return render_template(
        'catalog/categories.html',
        categories=categories,
        product_counts=counts,
        form_state=form_state,
    )


@bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id: int):
    category = Category.query.get_or_404(category_id)
    has_children = Category.query.filter_by(parent_id=category.id).first() is not None
    product_count = Product.query.filter_by(category_id=category.id).count()

    if has_children:
        flash('Нельзя удалить категорию, у которой есть вложенные категории.', 'danger')
        return redirect(url_for('catalog.manage_categories'))
    if product_count > 0:
        flash('Нельзя удалить категорию с привязанными блюдами. Сначала перенесите или удалите блюда.', 'danger')
        return redirect(url_for('catalog.manage_categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Категория удалена', 'success')
    return redirect(url_for('catalog.manage_categories'))


@bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    categories = Category.query.order_by(Category.name.asc()).all()
    if request.method == 'POST':
        data, errors = _extract_product_form(request.form)
        if errors:
            for error in errors:
                flash(error, 'warning')
            return render_template(
                'catalog/product_form.html',
                product=None,
                categories=categories,
                form_data=request.form.to_dict(),
            )
        product = Product(**data)
        image_file = request.files.get('image_file')
        image_path = _store_product_image(image_file)
        if image_path:
            product.image_url = image_path
        db.session.add(product)
        db.session.commit()
        flash('Блюдо создано', 'success')
        return redirect(url_for('catalog.list_products'))

    return render_template(
        'catalog/product_form.html',
        product=None,
        categories=categories,
        form_data={},
    )


@bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name.asc()).all()
    if request.method == 'POST':
        data, errors = _extract_product_form(request.form)
        if errors:
            for error in errors:
                flash(error, 'warning')
            return render_template(
                'catalog/product_form.html',
                product=product,
                categories=categories,
                form_data=request.form.to_dict(),
            )
        for field, value in data.items():
            setattr(product, field, value)
        image_file = request.files.get('image_file')
        image_path = _store_product_image(image_file, product.image_url)
        if image_path != product.image_url:
            product.image_url = image_path
        db.session.commit()
        flash('Блюдо обновлено', 'success')
        return redirect(url_for('catalog.list_products'))

    return render_template(
        'catalog/product_form.html',
        product=product,
        categories=categories,
        form_data=_product_to_form_data(product),
    )


@bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    try:
        image_path = product.image_url
        db.session.delete(product)
        db.session.commit()
        if image_path and not image_path.startswith(('http://', 'https://')):
            absolute = os.path.join(current_app.static_folder, image_path.replace('/', os.sep))
            if os.path.exists(absolute):
                try:
                    os.remove(absolute)
                except OSError:
                    pass
        flash('Блюдо удалено', 'success')
    except IntegrityError:
        db.session.rollback()
        flash(
            'Нельзя удалить блюдо: в заказах есть позиции, которые на него ссылаются. '
            'Сначала удалите или скорректируйте связанные заказы.',
            'danger',
        )
    return redirect(url_for('catalog.list_products'))


