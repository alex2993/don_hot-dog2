from datetime import datetime, date, time
import os
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.employees import Employee, Shift
from werkzeug.utils import secure_filename


bp = Blueprint('employees', __name__, url_prefix='/crm/employees')

POSITIONS = [
    'Директор', 'Бармен', 'Официант', 'Начальник склада', 'Кладовщик', 'Курьер',
    'Хостес', 'Бухгалтер', 'Повар', 'Шев повар', 'Су-шеф', 'Техничка', 'Разнорабочий'
]


@bp.route('/')
@login_required
def index():
    employees = Employee.query.order_by(Employee.full_name.asc()).all()
    return render_template('employees/index.html', employees=employees, positions=POSITIONS)


@bp.route('/create', methods=['POST'])
@login_required
def create_employee():
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    birth_date = request.form.get('birth_date')
    phone = request.form.get('phone')
    address = request.form.get('address')
    photo = request.files.get('photo')
    if not full_name or not position:
        flash('Заполните ФИО и должность', 'warning')
        return redirect(url_for('employees.index'))
    photo_path = None
    if photo and photo.filename:
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'employees')
        os.makedirs(uploads_dir, exist_ok=True)
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = secure_filename(f"{uuid4().hex}{ext}")
        photo.save(os.path.join(uploads_dir, filename))
        photo_path = f"/static/uploads/employees/{filename}"

    emp = Employee(
        full_name=full_name,
        position=position,
        birth_date=datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else None,
        phone=phone,
        address=address,
        photo_url=photo_path,
    )
    db.session.add(emp)
    db.session.commit()
    flash('Сотрудник добавлен', 'success')
    return redirect(url_for('employees.index'))


@bp.route('/delete/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id: int):
    # Проверка прав администратора
    role_name = (current_user.role.name if current_user.role else current_user.role_name or '').lower()
    if role_name != 'admin':
        flash('У вас нет прав для удаления сотрудников', 'danger')
        return redirect(url_for('employees.index'))

    emp = Employee.query.get_or_404(employee_id)

    # Удаление файла фото, если он существует
    if emp.photo_url:
        try:
            photo_path = emp.photo_url.replace('/static/', '')
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', photo_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception:
            pass  # Игнорируем ошибки при удалении файла

    db.session.delete(emp)
    db.session.commit()
    flash('Сотрудник удален', 'success')
    return redirect(url_for('employees.index'))


@bp.route('/update/<int:employee_id>', methods=['POST'])
@login_required
def update_employee(employee_id: int):
    emp = Employee.query.get_or_404(employee_id)
    emp.full_name = request.form.get('full_name') or emp.full_name
    emp.position = request.form.get('position') or emp.position
    birth_date = request.form.get('birth_date')
    emp.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else emp.birth_date
    emp.phone = request.form.get('phone') or emp.phone
    emp.address = request.form.get('address') or emp.address

    photo = request.files.get('photo')
    if photo and photo.filename:
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'employees')
        os.makedirs(uploads_dir, exist_ok=True)
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = secure_filename(f"{uuid4().hex}{ext}")
        photo.save(os.path.join(uploads_dir, filename))
        emp.photo_url = f"/static/uploads/employees/{filename}"

    db.session.commit()
    flash('Данные сотрудника обновлены', 'success')
    return redirect(url_for('employees.index'))


@bp.route('/schedule')
@login_required
def schedule():
    # Фильтр по месяцу
    year = int(request.args.get('y', date.today().year))
    month = int(request.args.get('m', date.today().month))
    shifts = Shift.query.filter(Shift.day >= date(year, month, 1)).all()
    emps = Employee.query.order_by(Employee.full_name.asc()).all()
    return render_template('employees/schedule.html', shifts=shifts, employees=emps, year=year, month=month)


@bp.route('/schedule/add', methods=['POST'])
@login_required
def add_shift():
    employee_id = int(request.form.get('employee_id'))
    day = datetime.strptime(request.form.get('day'), '%Y-%m-%d').date()
    start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
    end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
    shift = Shift(employee_id=employee_id, day=day, start_time=start_time, end_time=end_time)
    db.session.add(shift)
    db.session.commit()
    flash('Смена добавлена', 'success')
    return redirect(url_for('employees.schedule'))


@bp.route('/schedule/delete/<int:shift_id>', methods=['POST'])
@login_required
def delete_shift(shift_id: int):
    s = Shift.query.get_or_404(shift_id)
    db.session.delete(s)
    db.session.commit()
    flash('Смена удалена', 'success')
    return redirect(url_for('employees.schedule'))


