from pymongo import MongoClient

client = MongoClient('localhost', 27017, username='rosha', password='123456789', authSource='admin')
db = client['chatbot_db']
user_collection = db['auth_user']  # Assuming you're using the default Django auth user collection

users = user_collection.find()
for user in users:
    print(user)