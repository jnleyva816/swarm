# agents/weather_agent.py

import os
import re
import requests
from datetime import datetime, timedelta
from swarm import Agent
from utils.db_utils import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import analytics functions (assuming process_weather_analytics is defined elsewhere)
from agents.weather_analytics import process_weather_analytics

MAX_DATA_AGE = timedelta(hours=1)  # Data is considered outdated after 1 hour

def extract_city_name(user_request):
    user_request = user_request.lower().strip()
    print(f"[DEBUG] Extracting city name from user request: {user_request}")

    # Remove phrases like 'from database' or 'weather data for'
    user_request = re.sub(r"\s+from\s+(?:the\s+)?(?:database|weather database)$", "", user_request)
    user_request = re.sub(r"^(update|refresh)\s+(?:the\s+city\s+of\s+)?(?:weather\s+data\s+for\s+)?", "", user_request)
    user_request = re.sub(r"^(get|show|provide)\s+(?:the\s+)?(?:current\s+)?weather\s+for\s+", "", user_request)
    user_request = re.sub(r"^(get|show|provide)\s+(?:the\s+)?forecast\s+for\s+", "", user_request)

    # Attempt to extract city name
    match = re.search(r"^([\w\s,]+)$", user_request)
    if match:
        city_name = match.group(1).strip()
        print(f"[DEBUG] Extracted city name: {city_name}")
        return city_name
    else:
        print("[DEBUG] Could not extract city name.")
        return None

def fetch_weather_data(city_name):
    api_key = os.getenv('OPEN_WEATHER_API')
    if not api_key:
        print("[ERROR] OpenWeatherMap API key is not set.")
        return None, "OpenWeatherMap API key is not set."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    print(f"[DEBUG] Fetching weather data for '{city_name}' with params: {params}")
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        print(f"[DEBUG] API response status code: {response.status_code}")
        if response.status_code != 200:
            error_message = data.get('message', 'Error fetching weather data.')
            print(f"[ERROR] API Error: {error_message}")
            return None, f"API Error: {error_message}"
        return data, None
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None, f"Request failed: {e}"

def store_weather_data(weather_data):
    collection = db['weather_data']
    city_id = weather_data.get('id')  # Unique city ID from API
    current_time = datetime.utcnow()
    weather_data['modified_at'] = current_time

    try:
        # Check if the document exists
        existing_doc = collection.find_one({'id': city_id})
        if existing_doc:
            weather_data['created_at'] = existing_doc.get('created_at', current_time)
            # Update existing document
            collection.update_one(
                {'id': city_id},
                {'$set': weather_data}
            )
            print(f"[DEBUG] Updated weather data for city: {weather_data['name']}")
        else:
            # Set created_at for new document
            weather_data['created_at'] = current_time
            # Insert new document
            collection.insert_one(weather_data)
            print(f"[DEBUG] Inserted new weather data for city: {weather_data['name']}")
    except Exception as e:
        print(f"[ERROR] Failed to store weather data: {e}")

def update_weather_for_city(city_name):
    print(f"[DEBUG] Updating weather data for city: {city_name}")
    weather_data, error = fetch_weather_data(city_name)
    if error:
        print(f"[ERROR] {error}")
        return error
    else:
        store_weather_data(weather_data)
        return None

def get_weather_from_db(city_name):
    collection = db['weather_data']
    try:
        result = collection.find_one(
            {'name': {'$regex': f'^{re.escape(city_name)}$', '$options': 'i'}}
        )
        if not result:
            print(f"[DEBUG] No weather data found in database for city: {city_name}")
            return None
        data_timestamp = result.get('modified_at') or datetime.utcfromtimestamp(result['dt'])
        if datetime.utcnow() - data_timestamp > MAX_DATA_AGE:
            print(f"[DEBUG] Weather data for {city_name} is outdated.")
            return None
        print(f"[DEBUG] Retrieved weather data for {city_name} from database.")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to retrieve weather data from database: {e}")
        return None

def format_weather_response(weather_data):
    return (f"The current weather in {weather_data['name']}:\n"
            f"- Temperature: {weather_data['main']['temp']}°C\n"
            f"- Conditions: {weather_data['weather'][0]['description'].capitalize()}\n"
            f"- Humidity: {weather_data['main']['humidity']}%\n"
            f"- Wind Speed: {weather_data['wind']['speed']} m/s\n")

def list_cities_in_database():
    collection = db['weather_data']
    try:
        cities = collection.distinct('name')
        if not cities:
            return "There are no cities in the database."
        city_list = ', '.join(cities)
        print(f"[DEBUG] Retrieved cities from database: {city_list}")
        return f"The following cities are in the database:\n" + '\n'.join(f"- {city}" for city in cities)
    except Exception as e:
        print(f"[ERROR] Failed to list cities: {e}")
        return "Sorry, I couldn't retrieve the list of cities."

def get_average_temperature():
    collection = db['weather_data']
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "averageTemp": {"$avg": "$main.temp"}
            }}
        ]
        result = list(collection.aggregate(pipeline))
        if result:
            avg_temp = result[0]['averageTemp']
            print(f"[DEBUG] Calculated average temperature: {avg_temp}")
            return f"The average temperature among all cities is {avg_temp:.2f}°C."
        else:
            return "No temperature data available to calculate average."
    except Exception as e:
        print(f"[ERROR] Failed to calculate average temperature: {e}")
        return "Sorry, I couldn't calculate the average temperature."

def delete_city_data(city_name):
    collection = db['weather_data']
    try:
        result = collection.delete_one({'name': {'$regex': f'^{re.escape(city_name)}$', '$options': 'i'}})
        if result.deleted_count > 0:
            print(f"[DEBUG] Deleted weather data for city: {city_name}")
            return f"The weather data for **{city_name}** has been successfully deleted from the database."
        else:
            print(f"[DEBUG] No weather data found to delete for city: {city_name}")
            return f"No weather data found for **{city_name}** to delete."
    except Exception as e:
        print(f"[ERROR] Failed to delete city data: {e}")
        return "Sorry, I couldn't delete the city data."

def get_hottest_cities():
    collection = db['weather_data']
    try:
        # Retrieve top 5 hottest cities
        cursor = collection.find().sort('main.temp', -1).limit(5)
        cities = []
        for doc in cursor:
            cities.append(f"- **{doc['name']}** ({doc['main']['temp']}°C)")
        if cities:
            print(f"[DEBUG] Retrieved hottest cities: {cities}")
            return "Here are the hottest cities in the database:\n" + '\n'.join(cities)
        else:
            return "No data available to determine the hottest cities."
    except Exception as e:
        print(f"[ERROR] Failed to retrieve hottest cities: {e}")
        return "Sorry, I couldn't retrieve the list of hottest cities."

def get_coldest_cities():
    collection = db['weather_data']
    try:
        # Retrieve top 5 coldest cities
        cursor = collection.find().sort('main.temp', 1).limit(5)
        cities = []
        for doc in cursor:
            cities.append(f"- **{doc['name']}** ({doc['main']['temp']}°C)")
        if cities:
            print(f"[DEBUG] Retrieved coldest cities: {cities}")
            return "Here are the coldest cities in the database:\n" + '\n'.join(cities)
        else:
            return "No data available to determine the coldest cities."
    except Exception as e:
        print(f"[ERROR] Failed to retrieve coldest cities: {e}")
        return "Sorry, I couldn't retrieve the list of coldest cities."

def get_average_humidity():
    collection = db['weather_data']
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "averageHumidity": {"$avg": "$main.humidity"}
            }}
        ]
        result = list(collection.aggregate(pipeline))
        if result:
            avg_humidity = result[0]['averageHumidity']
            print(f"[DEBUG] Calculated average humidity: {avg_humidity}")
            return f"The average humidity across all cities is {avg_humidity:.2f}%."
        else:
            return "No humidity data available to calculate average."
    except Exception as e:
        print(f"[ERROR] Failed to calculate average humidity: {e}")
        return "Sorry, I couldn't calculate the average humidity."

def get_visibility(city_name):
    collection = db['weather_data']
    try:
        result = collection.find_one(
            {'name': {'$regex': f'^{re.escape(city_name)}$', '$options': 'i'}}
        )
        if result and 'visibility' in result:
            visibility = result['visibility']
            print(f"[DEBUG] Retrieved visibility for {city_name}: {visibility} meters")
            return f"The current visibility in {city_name} is {visibility} meters."
        else:
            return f"Visibility data for {city_name} is not available."
    except Exception as e:
        print(f"[ERROR] Failed to retrieve visibility data: {e}")
        return "Sorry, I couldn't retrieve the visibility data."

def update_city_data(city_name):
    print(f"[DEBUG] Updating weather data for city: {city_name}")
    error = update_weather_for_city(city_name)
    if error:
        print(f"[ERROR] Error updating weather for city {city_name}: {error}")
        return f"Sorry, I couldn't update the weather data for **{city_name}**. {error}"
    else:
        print(f"[DEBUG] Successfully updated weather data for city: {city_name}")
        return f"Weather data for **{city_name}** has been updated."

def process_weather_request(message):
    user_request = message.lower().strip()
    print(f"[DEBUG] Processing weather request: {user_request}")

    # Define patterns for different queries
    patterns = {
        'list_cities': r"^(list|show)\s+(all\s+)?(the\s+)?(cities|city)\s+(in|from)?\s+(the\s+)?database$",
        'average_temperature': r"^(average|mean)\s+(temperature|temp)$",
        'delete_city': r"^(delete|remove)\s+(?:the\s+)?(?:city\s+)?([\w\s,]+)$",
        'update_city': r"^(update|refresh)\s+(?:the\s+city\s+of\s+)?(?:weather\s+data\s+for\s+)?([\w\s,]+)$",
        'hottest_cities': r"^(hottest|warmest)\s+(cities|city)$",
        'coldest_cities': r"^(coldest|coolest)\s+(cities|city)$",
        'average_humidity': r"^(average|mean)\s+humidity$",
        'visibility': r"^(visibility)\s*(?:in\s+([\w\s,]+))?$",
        'weather_in_city': r"^(weather in|current weather in|what's the weather in|get weather for|show forecast for|get forecast for)\s+([\w\s,]+)$",
        'forecast_in_city': r"^(forecast in|show forecast in|get forecast for)\s+([\w\s,]+)$",
        'hottest': r"^(hottest)$",
        'humidity': r"^(humidity)$",
    }

    # Match user request against patterns
    for intent, pattern in patterns.items():
        match = re.match(pattern, user_request)
        if match:
            if intent == 'list_cities':
                print("[DEBUG] Detected request to list cities.")
                return list_cities_in_database()
            elif intent == 'average_temperature':
                print("[DEBUG] Detected request for average temperature.")
                return get_average_temperature()
            elif intent == 'delete_city':
                city_name = match.group(2).strip()
                print(f"[DEBUG] Detected request to delete city: {city_name}")
                return delete_city_data(city_name)
            elif intent == 'update_city':
                city_name = match.group(2).strip()
                print(f"[DEBUG] Detected request to update city: {city_name}")
                return update_city_data(city_name)
            elif intent == 'hottest_cities':
                print("[DEBUG] Detected request for hottest cities.")
                return get_hottest_cities()
            elif intent == 'coldest_cities':
                print("[DEBUG] Detected request for coldest cities.")
                return get_coldest_cities()
            elif intent == 'average_humidity':
                print("[DEBUG] Detected request for average humidity.")
                return get_average_humidity()
            elif intent == 'visibility':
                city_name = match.group(2).strip() if match.group(2) else None
                if city_name:
                    print(f"[DEBUG] Detected request for visibility in city: {city_name}")
                    return get_visibility(city_name)
                else:
                    # If city is not specified, provide average visibility or ask for city
                    return "Please specify a city to get its visibility data."
            elif intent == 'weather_in_city' or intent == 'forecast_in_city':
                city_name = match.group(2).strip()
                print(f"[DEBUG] Detected weather request for city: {city_name}")
                weather_data = get_weather_from_db(city_name)
                if not weather_data:
                    print(f"[DEBUG] Weather data not found or outdated for city: {city_name}. Fetching new data.")
                    error = update_weather_for_city(city_name)
                    if error:
                        print(f"[ERROR] Error updating weather for city {city_name}: {error}")
                        return error
                    weather_data = get_weather_from_db(city_name)
                    if not weather_data:
                        print(f"[ERROR] Could not fetch weather data for {city_name} after update.")
                        return f"Sorry, I couldn't fetch weather data for **{city_name}**."
                response = format_weather_response(weather_data)
                print(f"[DEBUG] Generated response for city {city_name}.")
                return response
            elif intent == 'hottest':
                print("[DEBUG] Detected request for hottest cities.")
                return get_hottest_cities()
            elif intent == 'humidity':
                print("[DEBUG] Detected request for average humidity.")
                return get_average_humidity()
    
    # If no patterns matched, attempt to extract city name for general weather queries
    city_name = extract_city_name(user_request)
    if city_name:
        print(f"[DEBUG] Attempting to provide weather for city: {city_name}")
        weather_data = get_weather_from_db(city_name)
        if not weather_data:
            print(f"[DEBUG] Weather data not found or outdated for city: {city_name}. Fetching new data.")
            error = update_weather_for_city(city_name)
            if error:
                print(f"[ERROR] Error updating weather for city {city_name}: {error}")
                return error
            weather_data = get_weather_from_db(city_name)
            if not weather_data:
                print(f"[ERROR] Could not fetch weather data for {city_name} after update.")
                return f"Sorry, I couldn't fetch weather data for **{city_name}**."
        response = format_weather_response(weather_data)
        print(f"[DEBUG] Generated response for city {city_name}.")
        return response
    else:
        # Handle unrecognized commands
        print("[DEBUG] Unrecognized command.")
        return "I'm sorry, I didn't understand your request. Could you please rephrase it?"

def transfer_back_to_router_agent(message):
    print("[DEBUG] Transferring back to router agent.")
    from agents.router_agent import router_agent
    return router_agent

weather_agent = Agent(
    name="Weather Agent",
    instructions="""
You are a helpful assistant that provides weather information and analytics to users.

Capabilities:
- Retrieve current weather data from the database and present it to the user.
- Perform analytics on the collected weather data, providing insights such as:
  - Hottest/coldest cities
  - Average temperatures
  - Average humidity
  - Wind speeds
  - Pressure readings
  - Visibility
  - Common conditions
  - Sunlight durations
- Manage the weather database by adding, updating, or deleting data.
- Provide lists of cities available in the database.

When the data is not available or outdated, you fetch new data from the API, store it in the database, and then present it to the user.

You should understand and respond to a variety of user requests without the need for specific functions for each type of query.
""",
    functions=[process_weather_request, transfer_back_to_router_agent]
)

