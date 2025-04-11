from flask import Flask, request, render_template
from pymongo import MongoClient
import datetime
import math

USING_DB = True

app = Flask(__name__)
print("Starting Flask app...\n\n")
if USING_DB:
    print("Connecting to database...")
    # Connecting to database
    client = MongoClient("localhost", 27017)
    db = client.Hazelwood
    # Confirm the connection
    if db is not None:
        print("Connected to database!")
        # Create collection if it doesn't exist
        if "Sensor Data" not in db.list_collection_names():
            db.create_collection("Sensor Data")
            print("Created collection 'Sensor Data'")
        else:
            print("Collection 'Sensor Data' already exists")
    else:
        print("Failed to connect to database")
        exit(1)


valid_measurement_types = [
  "pm10_standard",
  "pm25_standard",
  "pm100_standard",
  "aqi_pm25",
  "aqi_pm100",
  "temperature",
  "humidity",
  "pressure"
]


def process_data(sensor_type, value):
    datapoint = {
        "timestamp": datetime.datetime.now(),
        "measurement_type": sensor_type,
        "sensor_value": value,
    }
    print(f"Received {sensor_type} data: {value}")
    print(f"Datapoint: {datapoint}")
    if not USING_DB:
        return datapoint
    # Add AQI data to database
    return db["Sensor Data"].insert_one(datapoint)


@app.get("/")
def index_get():
    return "Hello World"


@app.post("/")
def index_post():
    data = request.get_json()
    name = data["name"]
    return f"Hello {name}\n"


@app.route("/name/<name>")
def name_route(name=None):
    return f"Hello {name}"


@app.get("/echo/<echo_msg>")
def echo(echo_msg):
    return echo_msg


@app.post("/sensor_data")
def process_sensor_data():
    json = request.get_json()
    if "type" not in json:
        return "Missing value", 400
    if "value" not in json:
        return "Missing measurement", 400

    measurement_type = json["type"]
    if measurement_type not in valid_measurement_types:
        # Create response with 400 status code
        return "Invalid measurement type", 400

    value = json["value"]
    process_data_response = process_data(measurement_type, value)
    print(f"process_data_response: {process_data_response}")
    # Create response with 200 status code
    return "OK", 200



@app.get("/sensor_data")
def show_sensor_data():
    if not USING_DB:
        return "No data available"
    data = {}
    for measurement_type in valid_measurement_types:
        last_ten = db["Sensor Data"].find({"measurement_type": measurement_type}).sort(
                "timestamp", -1
            ).limit(10)
        # Compute average
        print(f"Last 10 {measurement_type} values:")
        total = 0
        count = 0
        for doc in last_ten:
            print(doc["sensor_value"])
            total += doc["sensor_value"]
            count += 1
        if count > 0:
            average = total / count
            print(f"Average {measurement_type}: {average}")
            data[measurement_type] = average
        else:
            print(f"No {measurement_type} data available")
            data[measurement_type] = None
    return render_template("sensor_data.html", data=data)
