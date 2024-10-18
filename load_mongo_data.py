# load_mongo_data.py

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

    # Collections
    rss_feeds = db['rss_feeds']
    categories = db['categories']
    rss_items = db['rss_items']
    rss_item_categories = db['rss_item_categories']
    users = db['users']
    user_category_preferences = db['user_category_preferences']
    user_feed_preferences = db['user_feed_preferences']
    article_interactions = db['article_interactions']
    feed_views = db['feed_views']
    user_sessions = db['user_sessions']

    # Clear existing data
    rss_feeds.delete_many({})
    categories.delete_many({})
    rss_items.delete_many({})
    rss_item_categories.delete_many({})
    users.delete_many({})
    user_category_preferences.delete_many({})
    user_feed_preferences.delete_many({})
    article_interactions.delete_many({})
    feed_views.delete_many({})
    user_sessions.delete_many({})

    # Insert data into rss_feeds
    rss_feeds_data = [
        {'_id': 1, 'name': 'AI Daily', 'url': 'https://ai-daily.com/feed', 'description': 'Daily AI news and updates', 'site_link': 'https://ai-daily.com', 'language': 'en'},
        {'_id': 2, 'name': 'ML Weekly', 'url': 'https://mlweekly.com/rss', 'description': 'Weekly roundup of machine learning news', 'site_link': 'https://mlweekly.com', 'language': 'en'},
        {'_id': 3, 'name': 'IA Nouvelles', 'url': 'https://ia-nouvelles.fr/flux', 'description': "Actualités sur l'intelligence artificielle en français", 'site_link': 'https://ia-nouvelles.fr', 'language': 'fr'},
        {'_id': 4, 'name': 'Data Science Digest', 'url': 'https://datasciencedigest.com/feed', 'description': 'Comprehensive coverage of data science topics', 'site_link': 'https://datasciencedigest.com', 'language': 'en'},
        {'_id': 5, 'name': 'AI Ethics Blog', 'url': 'https://aiethicsblog.org/rss', 'description': 'Exploring ethical implications of AI', 'site_link': 'https://aiethicsblog.org', 'language': 'en'},
    ]
    rss_feeds.insert_many(rss_feeds_data)

    # Insert data into categories
    categories_data = [
        {'_id': 1, 'name': 'Machine Learning', 'description': 'News related to machine learning algorithms and techniques'},
        {'_id': 2, 'name': 'Natural Language Processing', 'description': 'Updates on NLP research and applications'},
        {'_id': 3, 'name': 'Computer Vision', 'description': 'Advancements in image and video processing using AI'},
        {'_id': 4, 'name': 'Ethics in AI', 'description': 'Discussions on ethical considerations in AI development and deployment'},
        {'_id': 5, 'name': 'Robotics', 'description': 'News about AI in robotics and automation'},
        {'_id': 6, 'name': 'AI in Healthcare', 'description': 'Applications of AI in medicine and healthcare'},
        {'_id': 7, 'name': 'Deep Learning', 'description': 'Focused on deep neural networks and related technologies'},
    ]
    categories.insert_many(categories_data)

    # Insert data into rss_items
    rss_items_data = [
        {'_id': 1, 'rss_feed_id': 1, 'title': 'New breakthrough in reinforcement learning', 'link': 'https://ai-daily.com/articles/reinforcement-learning-breakthrough', 'description': 'Researchers achieve significant progress in RL algorithms', 'content': 'Full content of the article...', 'published_date': '2023-04-15 09:30:00', 'author': 'Jane Doe'},
        {'_id': 2, 'rss_feed_id': 2, 'title': 'GPT-4 shows impressive results in medical diagnosis', 'link': 'https://mlweekly.com/news/gpt4-medical-diagnosis', 'description': "OpenAI's latest language model demonstrates potential in healthcare", 'content': 'Detailed article content...', 'published_date': '2023-04-14 14:45:00', 'author': 'John Smith'},
        {'_id': 3, 'rss_feed_id': 3, 'title': "L'IA générative révolutionne la création artistique", 'link': 'https://ia-nouvelles.fr/articles/ia-generative-art', 'description': "Comment l'IA transforme le processus créatif des artistes", 'content': "Contenu complet de l'article...", 'published_date': '2023-04-13 11:15:00', 'author': 'Marie Dupont'},
        {'_id': 4, 'rss_feed_id': 4, 'title': 'Advancements in Computer Vision for Autonomous Vehicles', 'link': 'https://datasciencedigest.com/articles/cv-autonomous-vehicles', 'description': 'Recent developments in CV improving self-driving car capabilities', 'content': 'Full article content...', 'published_date': '2023-04-16 10:00:00', 'author': 'Alex Johnson'},
        {'_id': 5, 'rss_feed_id': 5, 'title': 'The Ethics of AI in Hiring Processes', 'link': 'https://aiethicsblog.org/posts/ai-in-hiring', 'description': 'Examining the implications of using AI for job candidate selection', 'content': 'Detailed blog post content...', 'published_date': '2023-04-17 13:20:00', 'author': 'Samantha Lee'},
    ]
    rss_items.insert_many(rss_items_data)

    # Insert data into rss_item_categories
    rss_item_categories_data = [
        {'rss_item_id': 1, 'category_id': 1},
        {'rss_item_id': 1, 'category_id': 7},
        {'rss_item_id': 2, 'category_id': 2},
        {'rss_item_id': 2, 'category_id': 6},
        {'rss_item_id': 3, 'category_id': 1},
        {'rss_item_id': 3, 'category_id': 4},
        {'rss_item_id': 4, 'category_id': 3},
        {'rss_item_id': 4, 'category_id': 5},
        {'rss_item_id': 5, 'category_id': 4},
        {'rss_item_id': 5, 'category_id': 6},
    ]
    rss_item_categories.insert_many(rss_item_categories_data)

    # Insert data into users
    users_data = [
        {'_id': 1, 'username': 'alice_ai', 'email': 'alice@example.com', 'password_hash': 'hashed_password_1', 'created_at': '2023-01-01 10:00:00', 'last_login': '2023-04-15 14:30:00'},
        {'_id': 2, 'username': 'bob_ml', 'email': 'bob@example.com', 'password_hash': 'hashed_password_2', 'created_at': '2023-02-15 11:30:00', 'last_login': '2023-04-14 09:15:00'},
        {'_id': 3, 'username': 'charlie_nlp', 'email': 'charlie@example.com', 'password_hash': 'hashed_password_3', 'created_at': '2023-03-20 09:45:00', 'last_login': '2023-04-13 16:45:00'},
        {'_id': 4, 'username': 'dana_cv', 'email': 'dana@example.com', 'password_hash': 'hashed_password_4', 'created_at': '2023-03-25 14:00:00', 'last_login': '2023-04-16 11:30:00'},
        {'_id': 5, 'username': 'evan_ethics', 'email': 'evan@example.com', 'password_hash': 'hashed_password_5', 'created_at': '2023-04-01 08:30:00', 'last_login': '2023-04-17 10:45:00'},
    ]
    users.insert_many(users_data)

    # Insert data into user_category_preferences
    user_category_preferences_data = [
        {'user_id': 1, 'category_id': 1},
        {'user_id': 1, 'category_id': 2},
        {'user_id': 1, 'category_id': 7},
        {'user_id': 2, 'category_id': 1},
        {'user_id': 2, 'category_id': 3},
        {'user_id': 2, 'category_id': 5},
        {'user_id': 3, 'category_id': 2},
        {'user_id': 3, 'category_id': 4},
        {'user_id': 3, 'category_id': 6},
        {'user_id': 4, 'category_id': 3},
        {'user_id': 4, 'category_id': 5},
        {'user_id': 4, 'category_id': 7},
        {'user_id': 5, 'category_id': 4},
        {'user_id': 5, 'category_id': 6},
        {'user_id': 5, 'category_id': 1},
    ]
    user_category_preferences.insert_many(user_category_preferences_data)

    # Insert data into user_feed_preferences
    user_feed_preferences_data = [
        {'user_id': 1, 'rss_feed_id': 1},
        {'user_id': 1, 'rss_feed_id': 2},
        {'user_id': 1, 'rss_feed_id': 4},
        {'user_id': 2, 'rss_feed_id': 2},
        {'user_id': 2, 'rss_feed_id': 3},
        {'user_id': 2, 'rss_feed_id': 4},
        {'user_id': 3, 'rss_feed_id': 1},
        {'user_id': 3, 'rss_feed_id': 3},
        {'user_id': 3, 'rss_feed_id': 5},
        {'user_id': 4, 'rss_feed_id': 1},
        {'user_id': 4, 'rss_feed_id': 2},
        {'user_id': 4, 'rss_feed_id': 4},
        {'user_id': 5, 'rss_feed_id': 3},
        {'user_id': 5, 'rss_feed_id': 4},
        {'user_id': 5, 'rss_feed_id': 5},
    ]
    user_feed_preferences.insert_many(user_feed_preferences_data)

    # Insert data into article_interactions
    article_interactions_data = [
        {'user_id': 1, 'rss_item_id': 1, 'interaction_type': 'view', 'interaction_time': '2023-04-15 10:15:00'},
        {'user_id': 1, 'rss_item_id': 1, 'interaction_type': 'like', 'interaction_time': '2023-04-15 10:20:00'},
        {'user_id': 1, 'rss_item_id': 2, 'interaction_type': 'view', 'interaction_time': '2023-04-15 10:30:00'},
        {'user_id': 2, 'rss_item_id': 2, 'interaction_type': 'view', 'interaction_time': '2023-04-14 15:00:00'},
        {'user_id': 2, 'rss_item_id': 2, 'interaction_type': 'like', 'interaction_time': '2023-04-14 15:05:00'},
        {'user_id': 2, 'rss_item_id': 2, 'interaction_type': 'share', 'interaction_time': '2023-04-14 15:10:00'},
        {'user_id': 3, 'rss_item_id': 3, 'interaction_type': 'view', 'interaction_time': '2023-04-13 17:00:00'},
        {'user_id': 3, 'rss_item_id': 3, 'interaction_type': 'like', 'interaction_time': '2023-04-13 17:10:00'},
        {'user_id': 4, 'rss_item_id': 4, 'interaction_type': 'view', 'interaction_time': '2023-04-16 11:45:00'},
        {'user_id': 4, 'rss_item_id': 4, 'interaction_type': 'share', 'interaction_time': '2023-04-16 11:50:00'},
        {'user_id': 5, 'rss_item_id': 5, 'interaction_type': 'view', 'interaction_time': '2023-04-17 14:00:00'},
        {'user_id': 5, 'rss_item_id': 5, 'interaction_type': 'like', 'interaction_time': '2023-04-17 14:15:00'},
    ]
    article_interactions.insert_many(article_interactions_data)

    # Insert data into feed_views
    feed_views_data = [
        {'user_id': 1, 'rss_feed_id': 1, 'viewed_at': '2023-04-15 10:00:00'},
        {'user_id': 1, 'rss_feed_id': 2, 'viewed_at': '2023-04-15 10:25:00'},
        {'user_id': 2, 'rss_feed_id': 2, 'viewed_at': '2023-04-14 14:55:00'},
        {'user_id': 3, 'rss_feed_id': 3, 'viewed_at': '2023-04-13 16:50:00'},
        {'user_id': 4, 'rss_feed_id': 4, 'viewed_at': '2023-04-16 11:40:00'},
        {'user_id': 5, 'rss_feed_id': 5, 'viewed_at': '2023-04-17 13:55:00'},
    ]
    feed_views.insert_many(feed_views_data)

    # Insert data into user_sessions
    user_sessions_data = [
        {'user_id': 1, 'session_token': 'token_alice_1', 'created_at': '2023-04-15 14:30:00', 'expires_at': '2023-04-16 14:30:00'},
        {'user_id': 2, 'session_token': 'token_bob_1', 'created_at': '2023-04-14 09:15:00', 'expires_at': '2023-04-15 09:15:00'},
        {'user_id': 3, 'session_token': 'token_charlie_1', 'created_at': '2023-04-13 16:45:00', 'expires_at': '2023-04-14 16:45:00'},
        {'user_id': 4, 'session_token': 'token_dana_1', 'created_at': '2023-04-16 11:30:00', 'expires_at': '2023-04-17 11:30:00'},
        {'user_id': 5, 'session_token': 'token_evan_1', 'created_at': '2023-04-17 10:45:00', 'expires_at': '2023-04-18 10:45:00'},
    ]
    user_sessions.insert_many(user_sessions_data)

    print("Data successfully loaded into MongoDB.")

if __name__ == "__main__":
    main()

