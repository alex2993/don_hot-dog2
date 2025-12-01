from decimal import Decimal
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.inventory import (
    StockItem, StockMovement, Warehouse, StockBalance,
    Supplier, Purchase, PurchaseItem,
    InventoryDoc, InventoryLine
)


bp = Blueprint('inventory', __name__, url_prefix='/crm/inventory')


@bp.route('/')
@login_required
def index():
    warehouses = Warehouse.query.all()
    suppliers = Supplier.query.all()
    items = StockItem.query.all()
    moves = StockMovement.query.order_by(StockMovement.id.desc()).limit(20).all()
    return render_template('inventory/home.html', warehouses=warehouses, suppliers=suppliers, items=items, moves=moves)


@bp.route('/item/create', methods=['POST'])
@login_required
def create_item():
    item = StockItem(
        name=request.form.get('name'),
        unit=request.form.get('unit') or 'pcs',
        category=request.form.get('category') or None,
        item_type=request.form.get('item_type') or 'raw',
        sku=request.form.get('sku') or None,
        barcode=request.form.get('barcode') or None,
        purchase_price_plan=request.form.get('purchase_price_plan') or None,
        sale_price=request.form.get('sale_price') or None,
        is_alcohol='yes' if request.form.get('is_alcohol') == 'on' else 'no'
    )
    db.session.add(item)
    db.session.commit()
    flash('Номенклатура создана', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/move', methods=['POST'])
@login_required
def manual_move():
    item_id = int(request.form.get('item_id'))
    warehouse_id = int(request.form.get('warehouse_id'))
    delta = Decimal(request.form.get('delta') or '0')
    reason = request.form.get('reason') or 'Ручное движение'
    _apply_movement(warehouse_id, item_id, delta, 'manual', 0, reason)
    db.session.commit()
    flash('Движение зафиксировано', 'success')
    return redirect(url_for('inventory.index'))


def _apply_movement(warehouse_id: int, item_id: int, delta: Decimal, doc_type: str, doc_id: int, note: str | None = None):
    bal = StockBalance.query.filter_by(warehouse_id=warehouse_id, item_id=item_id).first()
    if not bal:
        bal = StockBalance(warehouse_id=warehouse_id, item_id=item_id, quantity=Decimal('0'))
        db.session.add(bal)
        db.session.flush()
    bal.quantity = (bal.quantity or 0) + Decimal(delta)
    mv = StockMovement(warehouse_id=warehouse_id, item_id=item_id, delta=delta, doc_type=doc_type, doc_id=doc_id, note=note)
    db.session.add(mv)


# Warehouses & Suppliers
@bp.route('/warehouse/create', methods=['POST'])
@login_required
def create_warehouse():
    name = request.form.get('name')
    if not name:
        flash('Название склада обязательно', 'warning')
        return redirect(url_for('inventory.index'))
    db.session.add(Warehouse(name=name))
    db.session.commit()
    flash('Склад создан', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/supplier/create', methods=['POST'])
@login_required
def create_supplier():
    name = request.form.get('name')
    contact = request.form.get('contact')
    if not name:
        flash('Название поставщика обязательно', 'warning')
        return redirect(url_for('inventory.index'))
    db.session.add(Supplier(name=name, contact=contact))
    db.session.commit()
    flash('Поставщик создан', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/warehouse/update/<int:warehouse_id>', methods=['POST'])
@login_required
def update_warehouse(warehouse_id: int):
    w = Warehouse.query.get_or_404(warehouse_id)
    name = request.form.get('name')
    if name:
        w.name = name
        db.session.commit()
        flash('Склад обновлен', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/supplier/update/<int:supplier_id>', methods=['POST'])
@login_required
def update_supplier(supplier_id: int):
    s = Supplier.query.get_or_404(supplier_id)
    name = request.form.get('name')
    contact = request.form.get('contact')
    if name:
        s.name = name
    s.contact = contact
    db.session.commit()
    flash('Поставщик обновлен', 'success')
    return redirect(url_for('inventory.index'))


# Purchase document
@bp.route('/purchase/new')
@login_required
def purchase_new():
    return render_template('inventory/purchase_edit.html',
                           purchase=None,
                           suppliers=Supplier.query.all(),
                           warehouses=Warehouse.query.all(),
                           items=StockItem.query.all())


@bp.route('/purchase/create', methods=['POST'])
@login_required
def purchase_create():
    supplier_id = request.form.get('supplier_id') or None
    warehouse_id = int(request.form.get('warehouse_id'))
    doc = Purchase(supplier_id=supplier_id, warehouse_id=warehouse_id, status='draft')
    db.session.add(doc)
    db.session.commit()
    flash('Черновик поступления создан', 'success')
    return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))


@bp.route('/purchase/<int:purchase_id>')
@login_required
def purchase_edit(purchase_id: int):
    doc = Purchase.query.get_or_404(purchase_id)
    return render_template('inventory/purchase_edit.html',
                           purchase=doc,
                           suppliers=Supplier.query.all(),
                           warehouses=Warehouse.query.all(),
                           items=StockItem.query.all())


@bp.route('/purchase/<int:purchase_id>/add', methods=['POST'])
@login_required
def purchase_add_item(purchase_id: int):
    doc = Purchase.query.get_or_404(purchase_id)
    item_id = int(request.form.get('item_id'))
    qty = Decimal(request.form.get('qty'))
    price = Decimal(request.form.get('price'))
    line = PurchaseItem(purchase_id=doc.id, item_id=item_id, qty=qty, price=price)
    db.session.add(line)
    db.session.commit()
    return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))


@bp.route('/purchase/<int:purchase_id>/update', methods=['POST'])
@login_required
def purchase_update(purchase_id: int):
    doc = Purchase.query.get_or_404(purchase_id)
    if doc.status == 'posted':
        flash('Документ проведен и недоступен для редактирования', 'warning')
        return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))
    supplier_id = request.form.get('supplier_id') or None
    warehouse_id = request.form.get('warehouse_id') or None
    doc.supplier_id = int(supplier_id) if supplier_id else None
    if warehouse_id:
        doc.warehouse_id = int(warehouse_id)
    db.session.commit()
    flash('Шапка документа обновлена', 'success')
    return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))


@bp.route('/purchase/<int:purchase_id>/line/<int:line_id>/delete', methods=['POST'])
@login_required
def purchase_delete_line(purchase_id: int, line_id: int):
    doc = Purchase.query.get_or_404(purchase_id)
    if doc.status == 'posted':
        flash('Документ проведен и недоступен для редактирования', 'warning')
        return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))
    line = PurchaseItem.query.get_or_404(line_id)
    db.session.delete(line)
    db.session.commit()
    flash('Позиция удалена', 'success')
    return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))


@bp.route('/purchase/<int:purchase_id>/post', methods=['POST'])
@login_required
def purchase_post(purchase_id: int):
    doc = Purchase.query.get_or_404(purchase_id)
    if doc.status == 'posted':
        flash('Документ уже проведен', 'info')
        return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))
    for line in doc.items:
        _apply_movement(doc.warehouse_id, line.item_id, line.qty, 'purchase', doc.id, 'Поступление')
    doc.status = 'posted'
    db.session.commit()
    flash('Поступление проведено', 'success')
    return redirect(url_for('inventory.purchase_edit', purchase_id=doc.id))


# Inventory document
@bp.route('/inventory/new')
@login_required
def inv_new():
    return render_template('inventory/inventory_edit.html',
                           doc=None,
                           warehouses=Warehouse.query.all(),
                           items=StockItem.query.all())


@bp.route('/inventory/create', methods=['POST'])
@login_required
def inv_create():
    warehouse_id = int(request.form.get('warehouse_id'))
    doc = InventoryDoc(warehouse_id=warehouse_id, status='draft')
    db.session.add(doc)
    db.session.commit()
    return redirect(url_for('inventory.inv_edit', inv_id=doc.id))


@bp.route('/inventory/<int:inv_id>')
@login_required
def inv_edit(inv_id: int):
    doc = InventoryDoc.query.get_or_404(inv_id)
    # balances for warehouse
    balances = StockBalance.query.filter_by(warehouse_id=doc.warehouse_id).all()
    bal_map = {b.item_id: b.quantity for b in balances}
    return render_template('inventory/inventory_edit.html',
                           doc=doc,
                           warehouses=Warehouse.query.all(),
                           items=StockItem.query.all(),
                           bal_map=bal_map)


@bp.route('/inventory/<int:inv_id>/fill', methods=['POST'])
@login_required
def inv_fill(inv_id: int):
    doc = InventoryDoc.query.get_or_404(inv_id)
    # create lines from balances
    balances = StockBalance.query.filter_by(warehouse_id=doc.warehouse_id).all()
    for b in balances:
        if not any(l.item_id == b.item_id for l in doc.lines):
            db.session.add(InventoryLine(doc_id=doc.id, item_id=b.item_id, counted_qty=b.quantity or 0))
    db.session.commit()
    return redirect(url_for('inventory.inv_edit', inv_id=doc.id))


@bp.route('/inventory/<int:inv_id>/set', methods=['POST'])
@login_required
def inv_set(inv_id: int):
    doc = InventoryDoc.query.get_or_404(inv_id)
    for line in doc.lines:
        val = request.form.get(f'counted_{line.id}')
        if val is not None:
            line.counted_qty = Decimal(val)
    db.session.commit()
    return redirect(url_for('inventory.inv_edit', inv_id=doc.id))


@bp.route('/inventory/<int:inv_id>/post', methods=['POST'])
@login_required
def inv_post(inv_id: int):
    doc = InventoryDoc.query.get_or_404(inv_id)
    if doc.status == 'posted':
        flash('Инвентаризация уже проведена', 'info')
        return redirect(url_for('inventory.inv_edit', inv_id=doc.id))
    balances = StockBalance.query.filter_by(warehouse_id=doc.warehouse_id).all()
    bal_map = {b.item_id: b.quantity for b in balances}
    for line in doc.lines:
        acct = Decimal(bal_map.get(line.item_id, 0) or 0)
        diff = Decimal(line.counted_qty or 0) - acct
        if diff != 0:
            _apply_movement(doc.warehouse_id, line.item_id, diff, 'inventory', doc.id, 'Корректировка инвентаризации')
    doc.status = 'posted'
    db.session.commit()
    flash('Инвентаризация проведена', 'success')
    return redirect(url_for('inventory.inv_edit', inv_id=doc.id))


