from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from models.crm import JobApplication


bp = Blueprint('applications', __name__, url_prefix='/crm/applications')


def _ensure_admin():
    role_name = None
    if current_user.role:
        role_name = (current_user.role.name or '').lower()
    else:
        role_name = (current_user.role_name or '').lower()
    if role_name != 'admin':
        abort(403)


@bp.route('/')
@login_required
def index():
    _ensure_admin()
    applications = JobApplication.query.order_by(JobApplication.id.desc()).all()
    return render_template('applications/index.html', applications=applications)


@bp.post('/<int:application_id>/comment')
@login_required
def update_comment(application_id: int):
    _ensure_admin()
    application = JobApplication.query.get_or_404(application_id)
    comment = (request.form.get('comment') or '').strip()
    application.comment = comment or None
    db.session.commit()
    flash('Комментарий обновлён.', 'success')
    return redirect(url_for('applications.index'))


@bp.post('/<int:application_id>/delete')
@login_required
def delete(application_id: int):
    _ensure_admin()
    application = JobApplication.query.get_or_404(application_id)
    db.session.delete(application)
    db.session.commit()
    flash('Заявка удалена.', 'info')
    return redirect(url_for('applications.index'))

