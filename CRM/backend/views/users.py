from typing import Dict, List, Optional

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required

from app import db
from models.user import User, Role

bp = Blueprint('users', __name__, url_prefix='/crm/users')

ROLE_DESCRIPTIONS: Dict[str, str] = {
    'user': 'Пользователь внешнего портала (без доступа к CRM)',
    'staff': 'Сотрудник CRM (базовые права)',
    'manager': 'Менеджер CRM (расширенные права)',
    'admin': 'Администратор (полный доступ)',
}

ROLE_ORDER = ['user', 'staff', 'manager', 'admin']


def _is_admin(user: Optional[User]) -> bool:
    if not user:
        return False
    role_name = (user.role.name if user.role else user.role_name or '').lower()
    return role_name == 'admin'


def _ensure_core_roles() -> List[Role]:
    core_names = set(ROLE_ORDER)
    existing_roles = Role.query.filter(Role.name.in_(core_names)).all()
    existing_names = {role.name for role in existing_roles}
    created = False
    for name in core_names:
        if name not in existing_names:
            db.session.add(Role(name=name))
            created = True
    if created:
        db.session.commit()
        existing_roles = Role.query.filter(Role.name.in_(core_names)).all()
    role_index = {name: idx for idx, name in enumerate(ROLE_ORDER)}
    return sorted(existing_roles, key=lambda r: role_index.get(r.name, len(role_index)))


def _normalize_role_name(user: User) -> str:
    if user.role:
        return (user.role.name or '').lower()
    return (user.role_name or '').lower()


@bp.before_request
def ensure_admin_access():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    if not _is_admin(current_user):
        abort(403)


@bp.route('/', methods=['GET'])
@login_required
def index():
    roles = _ensure_core_roles()
    users = User.query.order_by(User.full_name.is_(None), User.full_name.asc(), User.email.asc()).all()
    return render_template(
        'users/index.html',
        users=users,
        roles=roles,
        role_descriptions=ROLE_DESCRIPTIONS,
        normalize_role=_normalize_role_name,
    )


@bp.route('/<int:user_id>/role', methods=['POST'])
@login_required
def update_role(user_id: int):
    roles = _ensure_core_roles()
    user = User.query.get_or_404(user_id)
    role_id = request.form.get('role_id')
    full_name_raw = request.form.get('full_name', '')
    user.full_name = full_name_raw.strip() or None

    if role_id:
        role = Role.query.get(role_id)
        if not role:
            flash('Роль не найдена.', 'danger')
            return redirect(url_for('users.index'))
        user.role = role
        user.role_name = role.name
    else:
        staff_role = next((r for r in roles if r.name == 'staff'), None)
        user.role = staff_role
        user.role_name = 'staff'

    db.session.commit()
    flash(f'Роль пользователя «{user.full_name or user.email}» обновлена.', 'success')
    return redirect(url_for('users.index'))

