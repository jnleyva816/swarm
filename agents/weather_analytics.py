# agents/weather_analytics.py

import re
from utils.db_utils import db

def process_weather_analytics(user_request):
    user_request_lower = user_request.lower()
    print(f"[DEBUG] Processing weather analytics request: {user_request}")

    if "hottest" in user_request_lower:
        print("[DEBUG] Analytics request for hottest cities.")
        return get_hottest_cities()
    elif "coldest" in user_request_lower:
        print("[DEBUG] Analytics request for coldest cities.")
        return get_coldest_cities()
    elif "average temperature" in user_request_lower:
        print("[DEBUG] Analytics request for average temperature.")
        return get_average_temperature(user_request)
    # ... (Include other condition checks and corresponding function calls)
    else:
        print("[DEBUG] Analytics request not recognized.")
        return "Sorry, I didn't understand your analytics request."

def get_hottest_cities():
    print("[DEBUG] Calculating hottest cities.")
    pipeline = [
        {
            "$group": {
                "_id": "$name",
                "average_temp": {"$avg": "$main.temp"}
            }
        },
        {"$sort": {"average_temp": -1}},
        {"$limit": 5}
    ]
    try:
        results = db['weather_data'].aggregate(pipeline)
        hottest_cities = [f"{res['_id']}: {res['average_temp']:.2f}°C" for res in results]
        if not hottest_cities:
            print("[DEBUG] No weather data available for hottest cities.")
            return "No weather data available."
        response = "Top 5 hottest cities based on average temperature:\n" + "\n".join(hottest_cities)
        print("[DEBUG] Hottest cities calculated.")
        return response
    except Exception as e:
        print(f"[ERROR] Failed to calculate hottest cities: {e}")
        return "An error occurred while calculating the hottest cities."

def get_coldest_cities():
    print("[DEBUG] Calculating coldest cities.")
    pipeline = [
        {
            "$group": {
                "_id": "$name",
                "average_temp": {"$avg": "$main.temp"}
            }
        },
        {"$sort": {"average_temp": 1}},
        {"$limit": 5}
    ]
    try:
        results = db['weather_data'].aggregate(pipeline)
        coldest_cities = [f"{res['_id']}: {res['average_temp']:.2f}°C" for res in results]
        if not coldest_cities:
            print("[DEBUG] No weather data available for coldest cities.")
            return "No weather data available."
        response = "Top 5 coldest cities based on average temperature:\n" + "\n".join(coldest_cities)
        print("[DEBUG] Coldest cities calculated.")
        return response
    except Exception as e:
        print(f"[ERROR] Failed to calculate coldest cities: {e}")
        return "An error occurred while calculating the coldest cities."

def get_average_temperature(user_request):
    print("[DEBUG] Calculating average temperature.")
    match = re.search(r"average temperature in ([\w\s,]+)", user_request.lower())
    try:
        if match:
            city_name = match.group(1).strip()
            print(f"[DEBUG] Calculating average temperature for city: {city_name}")
            pipeline = [
                {"$match": {"name": {'$regex': f'^{city_name}$', '$options': 'i'}}},
                {
                    "$group": {
                        "_id": "$name",
                        "average_temp": {"$avg": "$main.temp"}
                    }
                }
            ]
            results = list(db['weather_data'].aggregate(pipeline))
            if results:
                avg_temp = results[0]['average_temp']
                response = f"The average temperature in {city_name.title()} is {avg_temp:.2f}°C."
                print("[DEBUG] Average temperature calculated.")
                return response
            else:
                print(f"[DEBUG] No weather data available for {city_name.title()}.")
                return f"No weather data available for {city_name.title()}."
        else:
            print("[DEBUG] Calculating average temperature across all cities.")
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "average_temp": {"$avg": "$main.temp"}
                    }
                }
            ]
            results = list(db['weather_data'].aggregate(pipeline))
            if results:
                avg_temp = results[0]['average_temp']
                response = f"The average temperature across all recorded cities is {avg_temp:.2f}°C."
                print("[DEBUG] Average temperature calculated.")
                return response
            else:
                print("[DEBUG] No weather data available.")
                return "No weather data available."
    except Exception as e:
        print(f"[ERROR] Failed to calculate average temperature: {e}")
        return "An error occurred while calculating the average temperature."

# ... (Add minimal debugging to other analytics functions in a similar manner)

