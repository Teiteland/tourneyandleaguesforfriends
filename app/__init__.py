from flask import Flask
from config import Config
from app.models.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    from app.cli import init_db, seed_data
    app.cli.add_command(init_db)
    app.cli.add_command(seed_data)

    with app.app_context():
        db.create_all()

    return app
