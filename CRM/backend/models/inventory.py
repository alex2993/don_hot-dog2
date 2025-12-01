from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app import db


class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StockItem(db.Model):
    __tablename__ = 'stock_items'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    unit = Column(String(20), default='pcs')
    category = Column(String(120))
    item_type = Column(String(50), default='raw')  # raw, product, semi, service
    sku = Column(String(100))
    barcode = Column(String(100))
    purchase_price_plan = Column(Numeric(12, 3))
    sale_price = Column(Numeric(12, 3))
    is_alcohol = Column(String(5))  # 'yes'/'no' for simplicity


class StockBalance(db.Model):
    __tablename__ = 'stock_balances'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    quantity = Column(Numeric(12, 3), default=0)

    item = relationship('StockItem')
    warehouse = relationship('Warehouse')


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    doc_type = Column(String(30), nullable=False)  # purchase, transfer, writeoff, inventory
    doc_id = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    delta = Column(Numeric(12, 3), nullable=False)
    note = Column(String(200))

    item = relationship('StockItem')
    warehouse = relationship('Warehouse')


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(200))


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    date = Column(Date, default=datetime.utcnow)
    status = Column(String(20), default='draft')  # draft, posted
    supplier = relationship('Supplier')
    warehouse = relationship('Warehouse')
    items = relationship('PurchaseItem', back_populates='purchase', cascade='all, delete-orphan')


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    qty = Column(Numeric(12, 3), nullable=False)
    price = Column(Numeric(12, 3), nullable=False)
    purchase = relationship('Purchase', back_populates='items')
    item = relationship('StockItem')


class Transfer(db.Model):
    __tablename__ = 'transfers'
    id = Column(Integer, primary_key=True)
    from_warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    to_warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    date = Column(Date, default=datetime.utcnow)
    status = Column(String(20), default='draft')
    from_warehouse = relationship('Warehouse', foreign_keys=[from_warehouse_id])
    to_warehouse = relationship('Warehouse', foreign_keys=[to_warehouse_id])
    items = relationship('TransferItem', back_populates='transfer', cascade='all, delete-orphan')


class TransferItem(db.Model):
    __tablename__ = 'transfer_items'
    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey('transfers.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    qty = Column(Numeric(12, 3), nullable=False)
    transfer = relationship('Transfer', back_populates='items')
    item = relationship('StockItem')


class WriteOff(db.Model):
    __tablename__ = 'writeoffs'
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    date = Column(Date, default=datetime.utcnow)
    reason = Column(String(200))
    status = Column(String(20), default='draft')
    warehouse = relationship('Warehouse')
    items = relationship('WriteOffItem', back_populates='writeoff', cascade='all, delete-orphan')


class WriteOffItem(db.Model):
    __tablename__ = 'writeoff_items'
    id = Column(Integer, primary_key=True)
    writeoff_id = Column(Integer, ForeignKey('writeoffs.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    qty = Column(Numeric(12, 3), nullable=False)
    writeoff = relationship('WriteOff', back_populates='items')
    item = relationship('StockItem')


class InventoryDoc(db.Model):
    __tablename__ = 'inventory_docs'
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    date = Column(Date, default=datetime.utcnow)
    status = Column(String(20), default='draft')
    warehouse = relationship('Warehouse')
    lines = relationship('InventoryLine', back_populates='doc', cascade='all, delete-orphan')


class InventoryLine(db.Model):
    __tablename__ = 'inventory_lines'
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('inventory_docs.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    counted_qty = Column(Numeric(12, 3), nullable=False)
    doc = relationship('InventoryDoc', back_populates='lines')
    item = relationship('StockItem')


class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    name = Column(String(200))
    items = relationship('RecipeItem', back_populates='recipe', cascade='all, delete-orphan')


class RecipeItem(db.Model):
    __tablename__ = 'recipe_items'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    item_id = Column(Integer, ForeignKey('stock_items.id'))
    qty = Column(Numeric(12, 3), nullable=False)
    recipe = relationship('Recipe', back_populates='items')
    item = relationship('StockItem')


