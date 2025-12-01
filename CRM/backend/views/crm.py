from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.crm import Customer, LoyaltyTier, Promotion


bp = Blueprint('crm', __name__, url_prefix='/crm/customers')


@bp.route('/')
@login_required
def index():
    customers = Customer.query.all()
    promotions = Promotion.query.all()
    tiers = LoyaltyTier.query.all()
    return render_template('crm/index.html', customers=customers, promotions=promotions, tiers=tiers)


@bp.route('/customer/create', methods=['POST'])
@login_required
def create_customer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    c = Customer(name=name, phone=phone)
    db.session.add(c)
    db.session.commit()
    flash('Клиент создан', 'success')
    return redirect(url_for('crm.index'))


