from datetime import datetime
from . import mongo
from bson import ObjectId

class User:
    """User model helper class for MongoDB"""
    @staticmethod
    def create(chat_id, initial_wallet=0.0):
        user = {
            'chat_id': str(chat_id),
            'wallet': float(initial_wallet),
            'created_at': datetime.utcnow(),
            'transactions': []  # List to store transaction history
        }
        mongo.db.users.insert_one(user)
        return user

    @staticmethod
    def get_by_chat_id(chat_id):
        return mongo.db.users.find_one({'chat_id': str(chat_id)})

    @staticmethod
    def update_wallet(chat_id, amount):
        """Update user wallet balance"""
        return mongo.db.users.update_one(
            {'chat_id': str(chat_id)},
            {
                '$inc': {'wallet': float(amount)},
                '$push': {
                    'transactions': {
                        'amount': float(amount),
                        'timestamp': datetime.utcnow(),
                        'type': 'credit' if amount > 0 else 'debit'
                    }
                }
            }
        )

class Group:
    """Group model helper class for MongoDB"""
    @staticmethod
    def create(chat_id, admin_id, cost, initial_profit=0.0):
        group = {
            'chat_id': str(chat_id),
            'admin_id': str(admin_id),
            'cost': float(cost),
            'profit': float(initial_profit),
            'created_at': datetime.utcnow(),
            'settings': {
                'welcome_message': '',
                'rules': '',
                'auto_kick': True
            }
        }
        mongo.db.groups.insert_one(group)
        return group

    @staticmethod
    def get_by_chat_id(chat_id):
        return mongo.db.groups.find_one({'chat_id': str(chat_id)})

    @staticmethod
    def get_admin_groups(admin_id):
        return list(mongo.db.groups.find({'admin_id': str(admin_id)}))

    @staticmethod
    def update_profit(chat_id, amount):
        return mongo.db.groups.update_one(
            {'chat_id': str(chat_id)},
            {'$inc': {'profit': float(amount)}}
        )

class Member:
    """Member model helper class for MongoDB"""
    @staticmethod
    def create(chat_id, group_chat_id, expiry):
        member = {
            'chat_id': str(chat_id),
            'group_chat_id': str(group_chat_id),
            'expiry': str(expiry),
            'joined_at': datetime.utcnow(),
            'status': 'active',
            'payment_history': []
        }
        mongo.db.members.insert_one(member)
        return member

    @staticmethod
    def get_active_members(group_chat_id):
        return list(mongo.db.members.find({
            'group_chat_id': str(group_chat_id),
            'status': 'active'
        }))

    @staticmethod
    def get_expired_members():
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return list(mongo.db.members.find({
            'expiry': {'$lt': current_time},
            'status': 'active'
        }))

    @staticmethod
    def update_expiry(chat_id, group_chat_id, new_expiry):
        return mongo.db.members.update_one(
            {
                'chat_id': str(chat_id),
                'group_chat_id': str(group_chat_id)
            },
            {
                '$set': {
                    'expiry': str(new_expiry),
                    'status': 'active'
                },
                '$push': {
                    'payment_history': {
                        'timestamp': datetime.utcnow(),
                        'expiry': str(new_expiry)
                    }
                }
            }
        )

# Create indexes for better query performance
def setup_indexes():
    """Create MongoDB indexes for better query performance"""
    # Users collection indexes
    mongo.db.users.create_index('chat_id', unique=True)
    
    # Groups collection indexes
    mongo.db.groups.create_index('chat_id', unique=True)
    mongo.db.groups.create_index('admin_id')
    
    # Members collection indexes
    mongo.db.members.create_index([('chat_id', 1), ('group_chat_id', 1)], unique=True)
    mongo.db.members.create_index('group_chat_id')
    mongo.db.members.create_index('expiry')

# Example document structures for reference:
user_structure = {
    'chat_id': str,  # Telegram chat ID
    'wallet': float,  # User's wallet balance
    'created_at': datetime,
    'transactions': [
        {
            'amount': float,
            'timestamp': datetime,
            'type': str  # 'credit' or 'debit'
        }
    ]
}

group_structure = {
    'chat_id': str,  # Telegram group chat ID
    'admin_id': str,  # Admin's chat ID
    'cost': float,  # Membership cost
    'profit': float,
    'created_at': datetime,
    'settings': {
        'welcome_message': str,
        'rules': str,
        'auto_kick': bool
    }
}

member_structure = {
    'chat_id': str,  # Member's chat ID
    'group_chat_id': str,  # Group's chat ID
    'expiry': str,  # Expiry datetime string
    'joined_at': datetime,
    'status': str,  # 'active' or 'expired'
    'payment_history': [
        {
            'timestamp': datetime,
            'expiry': str
        }
    ]
          }
