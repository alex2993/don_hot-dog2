import os
from datetime import timedelta
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from dotenv import load_dotenv


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# Try load .env from root or backend
for candidate in [os.path.join(ROOT_DIR, '.env'), os.path.join(BASE_DIR, '.env')]:
    if os.path.exists(candidate):
        load_dotenv(candidate)


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def create_app() -> Flask:
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'), static_folder=os.path.join(BASE_DIR, 'static'))

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/postgres')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['PORTAL_URL'] = os.getenv('PORTAL_URL', '#')

    # Mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '25'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models to register with SQLAlchemy metadata (absolute imports)
    from models import user, catalog, orders, crm, inventory, reviews  # noqa: F401

    # Blueprints (absolute imports)
    from views.site import bp as site_bp
    from views.auth import bp as auth_bp
    from views.dashboard import bp as dashboard_bp
    from views.catalog import bp as catalog_bp
    from views.orders import bp as orders_bp
    from views.crm import bp as crm_bp
    from views.inventory import bp as inventory_bp
    from views.employees import bp as employees_bp
    from views.sales import bp as sales_bp
    from views.delivery import bp as delivery_bp
    from views.applications import bp as applications_bp
    from views.users import bp as users_bp

    app.register_blueprint(site_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(crm_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(applications_bp)

    @app.route('/')
    def root():
        return redirect(url_for('site.home'))

    @app.before_request
    def restrict_portal_users():
        if not current_user.is_authenticated:
            return
        role_name = (current_user.role.name if current_user.role else current_user.role_name or '').lower()
        if role_name != 'user':
            return
        allowed_endpoints = {'auth.logout', 'auth.portal_info', 'auth.login', 'auth.register'}
        endpoint = request.endpoint or ''
        if endpoint in allowed_endpoints or endpoint.startswith('static') or endpoint.startswith('site.'):
            return
        return redirect(url_for('auth.portal_info'))

    # Ensure DB schema exists and critical columns present
    with app.app_context():
        try:
            # Create tables if they do not exist
            db.create_all()
            # Ensure uploads dir exists
            uploads_root = os.path.join(BASE_DIR, 'static', 'uploads')
            os.makedirs(os.path.join(uploads_root, 'employees'), exist_ok=True)
            os.makedirs(os.path.join(uploads_root, 'products'), exist_ok=True)
            os.makedirs(os.path.join(uploads_root, 'avatars'), exist_ok=True)
            # Ensure users.password_hash column exists (for fresh or legacy DBs)
            from sqlalchemy import inspect, text
            insp = inspect(db.engine)
            table_names = set(insp.get_table_names())
            if 'users' in table_names:
                user_cols = {c['name'] for c in insp.get_columns('users')}
                if 'password_hash' not in user_cols:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);'))
                    db.session.commit()
                if 'role_id' not in user_cols:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN role_id INTEGER;'))
                    db.session.commit()
                if 'role' not in user_cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'staff';"))
                    db.session.commit()
                else:
                    # Установить default и заполнить null значением 'staff'
                    try:
                        db.session.execute(text("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'staff';"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                    db.session.execute(text("UPDATE users SET role='staff' WHERE role IS NULL;"))
                    db.session.commit()
                if 'avatar_url' not in user_cols:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255);'))
                    db.session.commit()

            # Автопочинка схемы склада
            if 'stock_movements' in table_names:
                sm_cols = {c['name'] for c in insp.get_columns('stock_movements')}
                if 'doc_type' not in sm_cols:
                    db.session.execute(text("ALTER TABLE stock_movements ADD COLUMN doc_type VARCHAR(30);"))
                    db.session.commit()
                if 'doc_id' not in sm_cols:
                    db.session.execute(text("ALTER TABLE stock_movements ADD COLUMN doc_id INTEGER;"))
                    db.session.commit()
                if 'warehouse_id' not in sm_cols:
                    db.session.execute(text("ALTER TABLE stock_movements ADD COLUMN warehouse_id INTEGER;"))
                    db.session.commit()
                if 'note' not in sm_cols:
                    db.session.execute(text("ALTER TABLE stock_movements ADD COLUMN note VARCHAR(200);"))
                    db.session.commit()

            if 'stock_items' in table_names:
                si_cols = {c['name'] for c in insp.get_columns('stock_items')}
                if 'category' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN category VARCHAR(120);"))
                    db.session.commit()
                if 'item_type' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN item_type VARCHAR(50) DEFAULT 'raw';"))
                    db.session.commit()
                if 'sku' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN sku VARCHAR(100);"))
                    db.session.commit()
                if 'barcode' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN barcode VARCHAR(100);"))
                    db.session.commit()
                if 'purchase_price_plan' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN purchase_price_plan NUMERIC(12,3);"))
                    db.session.commit()
                if 'sale_price' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN sale_price NUMERIC(12,3);"))
                    db.session.commit()
                if 'is_alcohol' not in si_cols:
                    db.session.execute(text("ALTER TABLE stock_items ADD COLUMN is_alcohol VARCHAR(5);"))
                    db.session.commit()

            if 'products' in table_names:
                p_cols = {c['name'] for c in insp.get_columns('products')}
                if 'image_url' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(255);"))
                    db.session.commit()
                if 'description' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN description TEXT;"))
                    db.session.commit()
                if 'portion_grams' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN portion_grams INTEGER;"))
                    db.session.commit()
                if 'protein_100g' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN protein_100g NUMERIC(7,2);"))
                    db.session.commit()
                if 'fat_100g' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN fat_100g NUMERIC(7,2);"))
                    db.session.commit()
                if 'carb_100g' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN carb_100g NUMERIC(7,2);"))
                    db.session.commit()
                if 'kcal_100g' not in p_cols:
                    db.session.execute(text("ALTER TABLE products ADD COLUMN kcal_100g INTEGER;"))
                    db.session.commit()

            if 'job_applications' in table_names:
                ja_cols = {c['name'] for c in insp.get_columns('job_applications')}
                if 'comment' not in ja_cols:
                    db.session.execute(text("ALTER TABLE job_applications ADD COLUMN comment VARCHAR(500);"))
                    db.session.commit()

            # Автопочинка orders: добавление полей POS
            if 'orders' in table_names:
                o_cols = {c['name'] for c in insp.get_columns('orders')}
                if 'guest_count' not in o_cols:
                    db.session.execute(text("ALTER TABLE orders ADD COLUMN guest_count INTEGER DEFAULT 1;"))
                    db.session.commit()
                if 'waiter' not in o_cols:
                    db.session.execute(text("ALTER TABLE orders ADD COLUMN waiter VARCHAR(120);"))
                    db.session.commit()
                if 'comment' not in o_cols:
                    db.session.execute(text("ALTER TABLE orders ADD COLUMN comment VARCHAR(255);"))
                    db.session.commit()

            # Автопочинка delivery_orders: курьер
            if 'delivery_orders' in table_names:
                d_cols = {c['name'] for c in insp.get_columns('delivery_orders')}
                if 'courier_id' not in d_cols:
                    db.session.execute(text("ALTER TABLE delivery_orders ADD COLUMN courier_id INTEGER;"))
                    db.session.commit()
                if 'user_id' not in d_cols:
                    db.session.execute(text("ALTER TABLE delivery_orders ADD COLUMN user_id INTEGER;"))
                    db.session.commit()
        except Exception:
            # Don't break app startup on migration helper errors
            pass

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app


app = create_app()


