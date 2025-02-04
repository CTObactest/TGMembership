from flask import Flask
from application.models import db
from config import config
import os

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Import routes after app creation to avoid circular imports
    from application import route

    # Register blueprints if any
    # app.register_blueprint(some_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
