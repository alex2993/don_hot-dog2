import click
from app import app, db
from models import *  # noqa


@click.group()
def cli():
    pass


@cli.command('init-db')
def init_db():
    """Создать таблицы и базовые данные (роль admin, столы)."""
    with app.app_context():
        db.create_all()
        from models.user import Role
        if not Role.query.filter_by(name='admin').first():
            db.session.add(Role(name='admin'))
            db.session.commit()
        from models.orders import Table
        if not Table.query.first():
            for i in range(1, 7):
                db.session.add(Table(name=str(i)))
            db.session.commit()
    click.echo('DB initialized')


@cli.command('fix-db')
def fix_db():
    """Починить схему: добавить недостающие колонки, если их нет."""
    from sqlalchemy import inspect, text
    with app.app_context():
        insp = inspect(db.engine)
        cols = {c['name'] for c in insp.get_columns('users')}
        # Добавить users.password_hash, если отсутствует
        if 'password_hash' not in cols:
            db.session.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);'))
            db.session.commit()
        # Убедиться, что есть роль admin
        from models.user import Role
        if not Role.query.filter_by(name='admin').first():
            db.session.add(Role(name='admin'))
            db.session.commit()
    click.echo('DB fixed')


if __name__ == '__main__':
    cli()


