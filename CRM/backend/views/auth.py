from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models.user import User, Role


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        role_name = (current_user.role.name if current_user.role else current_user.role_name or '').lower()
        if role_name == 'user':
            return redirect(url_for('site.home'))
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Неверный email или пароль', 'danger')
        else:
            login_user(user, remember=True)
            role_name = (user.role.name if user.role else user.role_name or '').lower()
            if role_name == 'user':
                return redirect(url_for('site.home'))
            return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.home'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Пользователь уже существует', 'warning')
        else:
            role = Role.query.filter_by(name='user').first()
            user = User(email=email, full_name=full_name, role=role)
            # Заполним текстовую роль для совместимости
            user.role_name = 'user' if role else 'staff'
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Успешная регистрация. Войдите.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@bp.route('/portal-info')
@login_required
def portal_info():
    role_name = (current_user.role.name if current_user.role else current_user.role_name or '').lower()
    if role_name != 'user':
        return redirect(url_for('dashboard.index'))
    portal_url = current_app.config.get('PORTAL_URL') or url_for('site.home')
    return render_template('auth/portal_info.html', portal_url=portal_url)


