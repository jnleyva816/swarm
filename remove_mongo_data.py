# remove_mongo_data.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri:
        raise Exception("MONGODB_URI is not set in the .env file.")

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client['rss_feed_database']

    # Drop collections
    db['rss_feeds'].drop()
    db['categories'].drop()
    db['rss_items'].drop()
    db['rss_item_categories'].drop()
    db['users'].drop()
    db['user_category_preferences'].drop()
    db['user_feed_preferences'].drop()
    db['article_interactions'].drop()
    db['feed_views'].drop()
    db['user_sessions'].drop()

    print("All collections have been dropped from the database.")

if __name__ == "__main__":
    main()

