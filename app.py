from flask import Flask, request
from pymongo import MongoClient
import datetime

USING_DB = False

app = Flask(__name__)

# if (USING_DB):
#     # Connecting to database
#     client = MongoClient("localhost", 27017)
#     db = client.Hazelwood

# valid_sensor_types = ["VOC","PM"]

def process_data(sensor_type, data):
    datapoint = {
        "timestamp": datetime.datetime.now(),
        "sensor_type": sensor_type,
        "sensor_value": value
    }
    if not USING_DB:
        return datapoint
    # Add AQI data to database
    db["Sensor Data"].insert_one(datapoint)


@app.get("/")
def index_get():
    return 'Hello World'

@app.post("/")
def index_post():
    data = request.get_json()
    name = data['name']
    return f"Hello {name}\n"

@app.route("/name/<name>")
def name_route(name=None):
    return f"Hello {name}"


@app.get("/echo/<echo_msg>")
def echo(echo_msg):
    return echo_msg


# @app.route("/<sensor_type>", methods=["POST"])
# def process_sensor_data(sensor_type):
#     if sensor_type not in valid_sensor_types:
#         return "Invalid sensor type"
#     else:
#         process_data(sensor_type, requests)

