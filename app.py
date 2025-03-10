from flask import Flask
from pymongo import MongoClient
import datetime

USING_DB = FALSE

app = Flask(__name__)

if (USING_DB):
    # Connecting to database
    client = MongoClient("localhost", 27017)
    db = client.Hazelwood

@app.route("/", methods=['GET', 'POST'])
def index(name):
    if request.method == 'GET':
        return '<h1>Hello World</h1>'
    if request.method == 'POST':
        return f"<h1>Hello {name} </h1>"
    else:


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

