from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def form_an_answer(weather_for_a_day, requester_name, location):
    response = {
        "requester_name": requester_name,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "location": location,
        "weather": {
            "temp_c": (weather_for_a_day.get('temp') - 32) * 5 / 9,
            "wind_kph": weather_for_a_day.get('windspeed') * 0.621371,
            "pressure_mb": weather_for_a_day.get('pressure'),
            "humidity": weather_for_a_day.get('humidity')
        }
    }
    return response


@app.route('/weather')
def get_weather():
    BASE_URL = os.getenv('BASE_URL')
    API_KEY = os.getenv('API_KEY')
    API_TOKEN = os.getenv('API_TOKEN')
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON format"}), 400
    token = data.get('token')
    if token != API_TOKEN:
        return jsonify({"error": "Bad token."}), 400
    requester_name = data.get('requester_name')
    location = data.get('location')
    date = data.get('date')

    if location is None or date is None or requester_name is None:
        return jsonify({"error": "Location, date and requester_name are required."}), 400
    url = f"{BASE_URL}/{location}/{date}?key={API_KEY}&include=days&elements=temp,windspeed,pressure,humidity"
    response_weather_api = requests.get(url)
    if response_weather_api.status_code == requests.codes.ok:
        response = form_an_answer(response_weather_api.json().get('days')[0], requester_name, location)
        return jsonify(response), 200
    return jsonify({"error": response_weather_api.content.decode("utf-8")})


if __name__ == '__main__':
    app.run()
