from pymongo import MongoClient

def test_mongodb_connection():
    try:
        client = MongoClient('localhost', 27017, username='rosha', password='123456789', authSource='admin')
        db = client['chatbot_db']
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_mongodb_connection()
