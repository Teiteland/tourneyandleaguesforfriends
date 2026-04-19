from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.models.models import db

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)

    from app.cli import init_db, seed_data, create_admin, migrate_users
    app.cli.add_command(init_db)
    app.cli.add_command(seed_data)
    app.cli.add_command(create_admin)
    app.cli.add_command(migrate_users)

    return app
