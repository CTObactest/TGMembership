import os
from datetime import timedelta

class Config:
    """Application configuration."""
    
    # General Config
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-insecure-key-for-dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/telegrambot')
    
    # Koyeb Deployment
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    SERVER_NAME = os.getenv('KOYEB_DOMAIN')  # your-app.koyeb.app
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token_here')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_bot_username')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
    
    @property
    def WEBHOOK_URL(self):
        return f"https://{self.SERVER_NAME}{self.WEBHOOK_PATH}"
    
    # Payment Providers Configuration
    # Coinbase Commerce
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', 'your_coinbase_api_key')
    COINBASE_WEBHOOK_SECRET = os.getenv('COINBASE_WEBHOOK_SECRET', 'your_webhook_secret')
    
    # Flutterwave
    FLUTTERWAVE_SECRET_KEY = os.getenv('FLUTTERWAVE_SECRET_KEY', 'your_flutterwave_secret')
    FLUTTERWAVE_PUBLIC_KEY = os.getenv('FLUTTERWAVE_PUBLIC_KEY', 'your_flutterwave_public')
    FLUTTERWAVE_ENCRYPTION_KEY = os.getenv('FLUTTERWAVE_ENCRYPTION_KEY', 'your_encryption_key')
    
    # PayPal
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'your_paypal_client_id')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', 'your_paypal_secret')
    PAYPAL_ENV = os.getenv('PAYPAL_ENV', 'sandbox')  # or 'live'
    
    @property
    def PAYPAL_API_URL(self):
        if self.PAYPAL_ENV == 'live':
            return 'https://api-m.paypal.com'
        return 'https://api-m.sandbox.paypal.com'
    
    @property
    def PAYPAL_WEBHOOK_URL(self):
        if self.PAYPAL_ENV == 'live':
            return 'https://ipnpb.paypal.com/cgi-bin/webscr'
        return 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'
    
    # Payment Settings
    PLATFORM_FEE_PERCENT = float(os.getenv('PLATFORM_FEE_PERCENT', '15'))  # 15%
    MINIMUM_DEPOSIT = float(os.getenv('MINIMUM_DEPOSIT', '5'))  # $5
    MAXIMUM_DEPOSIT = float(os.getenv('MAXIMUM_DEPOSIT', '1000'))  # $1000
    MINIMUM_WITHDRAWAL = float(os.getenv('MINIMUM_WITHDRAWAL', '10'))  # $10
    WITHDRAWAL_FEE_PERCENT = float(os.getenv('WITHDRAWAL_FEE_PERCENT', '2.5'))  # 2.5%
    
    # Membership Settings
    DEFAULT_MEMBERSHIP_DURATION = timedelta(days=30)  # 30 days default
    MEMBERSHIP_GRACE_PERIOD = timedelta(days=1)  # 1 day grace period
    AUTO_KICK_EXPIRED = os.getenv('AUTO_KICK_EXPIRED', 'True').lower() in ('true', '1', 't')
    
    # URLs
    SUCCESS_REDIRECT_URL = os.getenv('SUCCESS_REDIRECT_URL', 'https://your-domain.com/success')
    CANCEL_REDIRECT_URL = os.getenv('CANCEL_REDIRECT_URL', 'https://your-domain.com/cancel')
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "300/hour"
    RATELIMIT_STORAGE_URL = MONGO_URI
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Error Reporting
    PROPAGATE_EXCEPTIONS = True
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    def get_payment_providers(self):
        """Get enabled payment providers based on configuration."""
        providers = []
        
        if self.COINBASE_API_KEY and self.COINBASE_API_KEY != 'your_coinbase_api_key':
            providers.append({
                'name': 'Crypto',
                'provider': 'coinbase',
                'enabled': True
            })
            
        if self.FLUTTERWAVE_SECRET_KEY and self.FLUTTERWAVE_SECRET_KEY != 'your_flutterwave_secret':
            providers.append({
                'name': 'Card',
                'provider': 'flutterwave',
                'enabled': True
            })
            
        if self.PAYPAL_CLIENT_ID and self.PAYPAL_CLIENT_ID != 'your_paypal_client_id':
            providers.append({
                'name': 'PayPal',
                'provider': 'paypal',
                'enabled': True
            })
            
        return providers

    def calculate_platform_fee(self, amount):
        """Calculate platform fee for a given amount."""
        return (amount * self.PLATFORM_FEE_PERCENT) / 100

    def calculate_withdrawal_fee(self, amount):
        """Calculate withdrawal fee for a given amount."""
        return (amount * self.WITHDRAWAL_FEE_PERCENT) / 100

# Initialize config
config = Config()
