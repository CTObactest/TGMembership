import requests
import json
from datetime import datetime
import hmac
import hashlib
from decouple import config
import logging
from coinbase_commerce import Client
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentAPI:
    def __init__(self):
        # Coinbase configuration
        self.coinbase_client = Client(api_key=config('COINBASE_API_KEY'))
        self.coinbase_webhook_secret = config('COINBASE_WEBHOOK_SECRET')
        
        # Flutterwave configuration
        self.flutterwave_secret = config('FLUTTERWAVE_SECRET_KEY')
        self.flutterwave_public = config('FLUTTERWAVE_PUBLIC_KEY')
        
        # PayPal configuration
        self.paypal_client_id = config('PAYPAL_CLIENT_ID')
        self.paypal_secret = config('PAYPAL_CLIENT_SECRET')
        self.paypal_base_url = config('PAYPAL_API_URL', default='https://api-m.paypal.com')
        
        # Common configuration
        self.redirect_url = config('SUCCESS_REDIRECT_URL')
        self.cancel_url = config('CANCEL_REDIRECT_URL')

    def get_paypal_access_token(self):
        """Get PayPal OAuth access token"""
        try:
            credentials = base64.b64encode(
                f"{self.paypal_client_id}:{self.paypal_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(
                f"{self.paypal_base_url}/v1/oauth2/token",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                return response.json()['access_token']
            return None
        except Exception as e:
            logger.error(f"PayPal token error: {str(e)}")
            return None

    def create_coinbase_charge(self, chat_id, amount=None):
        """Create Coinbase Commerce charge"""
        try:
            charge_data = {
                "name": "Telegram Bot Deposit",
                "description": f"Deposit for chat ID: {chat_id}",
                "metadata": {
                    "chat_id": str(chat_id)
                },
                "redirect_url": self.redirect_url,
                "cancel_url": self.cancel_url
            }
            
            if amount:
                charge_data.update({
                    "pricing_type": "fixed_price",
                    "local_price": {
                        "amount": str(amount),
                        "currency": "USD"
                    }
                })
            else:
                charge_data["pricing_type"] = "no_price"
            
            charge = self.coinbase_client.charge.create(**charge_data)
            return charge.hosted_url
        except Exception as e:
            logger.error(f"Coinbase charge error: {str(e)}")
            return None

    def create_flutterwave_charge(self, chat_id, email, amount):
        """Create Flutterwave payment link"""
        try:
            headers = {
                'Authorization': f'Bearer {self.flutterwave_secret}',
                'Content-Type': 'application/json',
            }
            
            data = {
                "tx_ref": f"tg-{chat_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": str(amount),
                "currency": "USD",
                "redirect_url": self.redirect_url,
                "meta": {
                    "chat_id": str(chat_id)
                },
                "customer": {
                    "email": email
                },
                "customizations": {
                    "title": "Telegram Bot Deposit",
                    "description": f"Deposit for chat ID: {chat_id}"
                }
            }
            
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()['data']['link']
            return None
        except Exception as e:
            logger.error(f"Flutterwave charge error: {str(e)}")
            return None

    def create_paypal_order(self, chat_id, amount):
        """Create PayPal order"""
        try:
            access_token = self.get_paypal_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": str(amount)
                    },
                    "custom_id": str(chat_id)
                }],
                "application_context": {
                    "return_url": self.redirect_url,
                    "cancel_url": self.cancel_url
                }
            }
            
            response = requests.post(
                f"{self.paypal_base_url}/v2/checkout/orders",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                for link in response.json()['links']:
                    if link['rel'] == 'approve':
                        return link['href']
            return None
        except Exception as e:
            logger.error(f"PayPal order error: {str(e)}")
            return None

    def verify_coinbase_signature(self, payload, signature):
        """Verify Coinbase webhook signature"""
        try:
            expected_sig = hmac.new(
                self.coinbase_webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_sig, signature)
        except Exception as e:
            logger.error(f"Coinbase signature verification error: {str(e)}")
            return False

    def verify_flutterwave_transaction(self, transaction_id):
        """Verify Flutterwave transaction"""
        try:
            headers = {
                'Authorization': f'Bearer {self.flutterwave_secret}'
            }
            
            response = requests.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()['data']
            return None
        except Exception as e:
            logger.error(f"Flutterwave verification error: {str(e)}")
            return None

    def verify_paypal_payment(self, order_id):
        """Verify PayPal payment"""
        try:
            access_token = self.get_paypal_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.paypal_base_url}/v2/checkout/orders/{order_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"PayPal verification error: {str(e)}")
            return None

# Initialize payment API
payment_api = PaymentAPI()
