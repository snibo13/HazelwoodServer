from flask import Flask, request
from pymongo import MongoClient
import datetime

USING_DB = False

app = Flask(__name__)

if (USING_DB):
    # Connecting to database
    client = MongoClient("localhost", 27017)
    db = client.Hazelwood

@app.get("/")
def index_get():
    return '<h1>Hello World</h1>'

@app.post("/")
def index_post():
    data = request.get_json()
    name = data['name']
    return f"<h1>Hello {name} </h1>"

@app.route("/name/<name>")
def name_route(name=None):
    return f"<h1>Hello {name} </h1>"

@app.route("/aqi", methods=["POST"])
def process_aqi(data):
    datapoint = {
        "timestamp": datetime.datetime.now(),
        "sensor_type": "AQI",
        "sensor_value": value
    }
    if not USING_DB:
        return datapoint
    # Add AQI data to database
    db["Sensor Data"].insert_one(datapoint)

