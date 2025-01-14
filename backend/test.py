import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)

client = MongoClient("mongodb+srv://izzat:dbpa$$word1234@cluster0.cvhz3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)
