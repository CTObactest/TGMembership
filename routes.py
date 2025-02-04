from flask import Blueprint, request, jsonify, current_app
import telebot
import logging
from coinbase_commerce.webhook import Webhook
from coinbase_commerce.error import WebhookInvalidPayload, SignatureVerificationError
import requests
from datetime import datetime
from bson.objectid import ObjectId
from . import mongo
import os

# Create blueprint
main_bp = Blueprint('main', __name__)

# Setup logging
logging.basicConfig(
    filename='flow.log', 
    encoding='utf-8', 
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Initialize bot
secret = "tgapi/v2"
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'), threaded=False)

# Update webhook for Koyeb
koyeb_domain = os.getenv('KOYEB_DOMAIN')
webhook_url = f"https://{koyeb_domain}/{secret}"
bot.remove_webhook()
bot.set_webhook(url=webhook_url)

def credit_payment(chat_id, amount):
    """Credit user account after successful payment"""
    try:
        # Update user balance in MongoDB
        mongo.db.users.update_one(
            {'chat_id': str(chat_id)},
            {'$inc': {'balance': float(amount)},
             '$push': {
                 'transactions': {
                     'amount': float(amount),
                     'type': 'credit',
                     'timestamp': datetime.utcnow()
                 }
             }
            },
            upsert=True
        )
        
        # Send confirmation message
        bot.send_message(
            chat_id,
            f"Payment credited! Amount: ${amount:.2f}\nYour payment has been processed successfully."
        )
        return True
    except Exception as e:
        logger.error(f"Credit error: {str(e)}")
        return False

@main_bp.route(f'/{secret}', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook requests"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

@main_bp.route("/coinbase-webhook", methods=['POST'])
def coinbase_webhook():
    """Handle Coinbase Commerce webhooks"""
    try:
        request_data = request.data.decode('utf-8')
        request_sig = request.headers.get('X-CC-Webhook-Signature', None)
        
        event = Webhook.construct_event(
            request_data, 
            request_sig, 
            current_app.config['COINBASE_WEBHOOK_SECRET']
        )
        
        if event.type == "charge:confirmed":
            # Process confirmed payment
            charge_data = event.data
            chat_id = charge_data.metadata.get('chat_id')
            amount = float(charge_data.pricing.local.amount)
            
            if chat_id and amount:
                credit_payment(chat_id, amount)
                
        return jsonify({"status": "success"}), 200
    except (WebhookInvalidPayload, SignatureVerificationError) as e:
        logger.error(f"Coinbase webhook error: {str(e)}")
        return str(e), 400

@main_bp.route("/flutterwave-webhook", methods=['POST'])
def flutterwave_webhook():
    """Handle Flutterwave webhooks"""
    try:
        payload = request.get_json()
        
        if payload.get('status') == 'successful':
            # Verify transaction
            tx_id = payload.get('id')
            verify_url = f"https://api.flutterwave.com/v3/transactions/{tx_id}/verify"
            headers = {'Authorization': f'Bearer {current_app.config["FLUTTERWAVE_SECRET_KEY"]}'}
            
            response = requests.get(verify_url, headers=headers).json()
            
            if (response['status'] == 'success' and 
                response['data']['status'] == 'successful'):
                
                chat_id = response['data']['meta'].get('chat_id')
                amount = float(response['data']['amount'])
                
                if chat_id and amount:
                    credit_payment(chat_id, amount)
                    
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Flutterwave webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@main_bp.route("/paypal-webhook", methods=['POST'])
def paypal_webhook():
    """Handle PayPal IPN webhooks"""
    try:
        # Verify IPN message
        verify_url = current_app.config['PAYPAL_VERIFY_URL']
        payload = request.form.to_dict()
        
        # Add CMD to payload
        payload['cmd'] = '_notify-validate'
        
        # Send verification request to PayPal
        verification = requests.post(verify_url, data=payload)
        
        if verification.text == 'VERIFIED':
            if payload.get('payment_status') == 'Completed':
                chat_id = payload.get('custom')  # chat_id stored in custom field
                amount = float(payload.get('mc_gross', 0))
                
                if chat_id and amount:
                    credit_payment(chat_id, amount)
                    
        return "OK", 200
    except Exception as e:
        logger.error(f"PayPal webhook error: {str(e)}")
        return str(e), 400

@bot.message_handler(commands=['deposit'])
def deposit_handler(message):
    """Handle deposit command"""
    markup = telebot.types.InlineKeyboardMarkup()
    
    # Add payment method buttons
    markup.add(
        telebot.types.InlineKeyboardButton(
            "Crypto (Coinbase)", 
            callback_data="paymethod_coinbase"
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            "Card (Flutterwave)", 
            callback_data="paymethod_flutterwave"
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            "PayPal", 
            callback_data="paymethod_paypal"
        )
    )
    
    bot.send_message(
        message.chat.id,
        "Choose your payment method:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('paymethod_'))
def payment_method_handler(call):
    """Handle payment method selection"""
    chat_id = call.from_user.id
    method = call.data.split('_')[1]
    
    # Create payment links based on method
    if method == 'coinbase':
        charge = create_coinbase_charge(chat_id)
        payment_link = charge.hosted_url
    elif method == 'flutterwave':
        payment_link = create_flutterwave_link(chat_id)
    elif method == 'paypal':
        payment_link = create_paypal_link(chat_id)
    else:
        bot.answer_callback_query(call.id, "Invalid payment method")
        return

    if payment_link:
        bot.send_message(
            chat_id,
            f"Click the link below to complete your payment:\n{payment_link}"
        )
    else:
        bot.send_message(
            chat_id,
            "Sorry, there was an error generating the payment link. Please try again."
        )
