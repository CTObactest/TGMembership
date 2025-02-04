from flask import Flask
from flask_pymongo import PyMongo
from telegram.ext import Updater, Dispatcher
from decouple import config
import os

# Initialize MongoDB
mongo = PyMongo()

def create_app():
    """Construct the core application with MongoDB and Telegram bot."""
    server = Flask(__name__, instance_relative_config=False)
    
    # Configure MongoDB
    # Use environment variable for Koyeb deployment
    mongodb_uri = os.getenv('MONGODB_URI', config('MONGODB_URI', default='mongodb://localhost:27017/telegrambot'))
    server.config['MONGO_URI'] = mongodb_uri
    
    # Configure host and port for Koyeb
    server.config['HOST'] = '0.0.0.0'
    server.config['PORT'] = int(os.getenv('PORT', 8080))
    
    # Initialize MongoDB
    mongo.init_app(server)
    
    # Initialize Telegram bot
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', config('TELEGRAM_BOT_TOKEN', default=''))
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    # Payment configurations
    server.config['FLUTTERWAVE_SECRET_KEY'] = os.getenv('FLUTTERWAVE_SECRET_KEY', config('FLUTTERWAVE_SECRET_KEY', default=''))
    server.config['FLUTTERWAVE_PUBLIC_KEY'] = os.getenv('FLUTTERWAVE_PUBLIC_KEY', config('FLUTTERWAVE_PUBLIC_KEY', default=''))
    server.config['PAYPAL_CLIENT_ID'] = os.getenv('PAYPAL_CLIENT_ID', config('PAYPAL_CLIENT_ID', default=''))
    server.config['PAYPAL_CLIENT_SECRET'] = os.getenv('PAYPAL_CLIENT_SECRET', config('PAYPAL_CLIENT_SECRET', default=''))
    server.config['CRYPTO_API_KEY'] = os.getenv('CRYPTO_API_KEY', config('CRYPTO_API_KEY', default=''))
    
    with server.app_context():
        # Import routes and handlers
        from .routes import main_bp
        from .telegram_handlers import register_handlers
        
        # Register blueprints
        server.register_blueprint(main_bp)
        
        # Register telegram handlers
        register_handlers(dispatcher)
        
        # Start telegram bot polling in a separate thread
        updater.start_polling()
        
        return server

# For Koyeb deployment
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT']
      )
