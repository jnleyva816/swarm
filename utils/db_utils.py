# utils/db_utils.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mongo_uri = os.getenv('MONGODB_URI')
if not mongo_uri:
    raise Exception("MONGODB_URI is not set in the .env file.")

client = MongoClient(mongo_uri)
db = client['rss_feed_database']

def run_mongodb_query(collection_name, query, projection=None):
    collection = db[collection_name]
    results = collection.find(query, projection)
    
    records = list(results)
    if not records:
        return "No results found."
    
    result_str = ""
    for record in records:
        record.pop('_id', None)
        result_str += str(record) + "\n"
    
    return result_str

