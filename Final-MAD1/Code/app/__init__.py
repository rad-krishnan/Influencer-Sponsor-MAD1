from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = '21f3003252'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Define the default login view for the LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.views.admin import admin_bp
    from app.views.sponsor import sponsor_bp
    from app.views.influencer import influencer_bp
    from app.views.auth import auth_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(sponsor_bp, url_prefix='/sponsor')
    app.register_blueprint(influencer_bp, url_prefix='/influencer')

    # Default route to redirect to login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
