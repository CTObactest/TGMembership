# Telegram Membership Bot

A Telegram bot that manages paid group memberships with support for Crypto (Coinbase Commerce), Card payments (Flutterwave), and PayPal. Built with Flask and MongoDB, deployed on Koyeb.

## Features

- Multiple payment method support (Crypto, Cards, PayPal)
- Automated membership management
- Configurable platform fees
- Automatic expiry handling
- Member tracking and analytics
- Secure payment processing
- Easy deployment to Koyeb

## Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Telegram Bot Token
- Payment provider accounts:
  - Coinbase Commerce account
  - Flutterwave account
  - PayPal Business account

## Environment Variables for Koyeb

Create these environment variables in your Koyeb dashboard:

```env
# Flask Configuration
FLASK_SECRET_KEY=your_long_random_secure_secret_key
FLASK_DEBUG=False
PORT=8080
HOST=0.0.0.0

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@your-cluster.mongodb.net/dbname

# Koyeb Configuration
KOYEB_DOMAIN=your-app-name.koyeb.app

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username
WEBHOOK_PATH=/webhook

# Coinbase Commerce Configuration
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_WEBHOOK_SECRET=your_coinbase_webhook_secret

# Flutterwave Configuration
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret_key
FLUTTERWAVE_PUBLIC_KEY=your_flutterwave_public_key
FLUTTERWAVE_ENCRYPTION_KEY=your_flutterwave_encryption_key

# PayPal Configuration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_ENV=live  # or 'sandbox' for testing

# Payment Settings
PLATFORM_FEE_PERCENT=15
MINIMUM_DEPOSIT=5
MAXIMUM_DEPOSIT=1000
MINIMUM_WITHDRAWAL=10
WITHDRAWAL_FEE_PERCENT=2.5

# Membership Settings
AUTO_KICK_EXPIRED=true

# Redirect URLs
SUCCESS_REDIRECT_URL=https://your-domain.com/success
CANCEL_REDIRECT_URL=https://your-domain.com/cancel

# Logging
LOG_LEVEL=INFO
```

## Installation & Local Development

1. Clone the repository:
```bash
git clone https://github.com/CTObactest/TGMembership
cd telegram-membership-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your environment variables.

5. Run the application:
```bash
python app.py
```

## Deployment to Koyeb

1. Push your code to GitHub

2. Connect to Koyeb:
   - Create a new Koyeb account if you don't have one
   - Go to the Koyeb dashboard
   - Click "Create App"
   - Select GitHub as your deployment method
   - Choose your repository
   - Configure the environment variables listed above

3. Deploy:
   - Select Python as the runtime
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `python app.py`
   - Click "Deploy"

## Project Structure

```
telegram-membership-bot/
├── app.py
├── config.py
├── requirements.txt
├── Procfile
├── .env
├── .gitignore
└── application/
    ├── __init__.py
    ├── models.py
    ├── routes.py
    ├── payments_api.py
    └── telegram_handlers.py
```

## Required Python Packages

```txt
flask
flask-pymongo
python-telegram-bot
python-decouple
requests
coinbase-commerce
pymongo[srv]
dnspython
```

## Setting Up Payment Providers

### Coinbase Commerce
1. Create a Coinbase Commerce account
2. Generate an API key
3. Set up webhook endpoint
4. Add API key and webhook secret to environment variables

### Flutterwave
1. Create a Flutterwave account
2. Get your API keys from the dashboard
3. Configure webhook URL
4. Add API keys to environment variables

### PayPal
1. Create a PayPal Business account
2. Generate API credentials
3. Configure IPN or webhook URL
4. Add client ID and secret to environment variables

## Additional Configuration

- Platform fees can be adjusted using `PLATFORM_FEE_PERCENT`
- Minimum withdrawal amount set by `MINIMUM_WITHDRAWAL`
- Auto-kick expired members controlled by `AUTO_KICK_EXPIRED`
- Logging level can be configured with `LOG_LEVEL`

## Security Considerations

- All API keys and secrets should be kept secure
- Use HTTPS for all webhook endpoints
- Implement rate limiting for API endpoints
- Verify webhook signatures for all payment providers
- Monitor logs for suspicious activities

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
