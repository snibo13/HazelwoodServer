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

        if "Devices" not in db.list_collection_names():
            db.create_collection("Devices")
            print("Created collection 'Devices'")

    else:
        print("Failed to connect to database")
        exit(1)


valid_measurement_types = [
    "pm25_standard",
    "pm100_standard",
    "aqi_pm25",
    "aqi_pm100",
    "temperature",
    "humidity",
]


def process_data(device_name, sensor_type, value):
    datapoint = {
        "timestamp": datetime.datetime.now(),
        "measurement_type": sensor_type,
        "sensor_value": value,
        "device_name": device_name,
    }
    print(f"Received {sensor_type} data: {value}")
    print(f"Datapoint: {datapoint}")
    if not USING_DB:
        return datapoint
    # Add AQI data to database
    return db["Sensor Data"].insert_one(datapoint)


@app.get("/sensor_data")
def index_get():
    if not USING_DB:
        return "No data available"

    # Get all devices in the database
    devices = db["Sensor Data"].distinct("device_name")
    print(f"Devices: {devices}")
    points = []
    for device in devices:
        print(f"Device: {device}")

        last_ten = list(
            db["Sensor Data"]
            .find({"measurement_type": "aqi_pm25", "device_name": device})
            .sort("timestamp", -1)
            .limit(10)
        )

        quality = sum(last_ten) / len(last_ten) if last_ten else 0
        print(f"Last ten AQI values: {last_ten}")
        print(f"Average AQI: {quality}")

        if quality > 0:
            quality = math.ceil(quality / 10) * 10
        else:
            quality = 0
        print(f"Rounded AQI: {quality}")

        dev = db["Devices"].find_one({"device_name": device})
        if dev is None:
            print(f"Device {device} not found in database")
            continue

        point = {
            "device_name": device,
            "lon": dev["long"],
            "lat": dev["lat"],
            "device_quality": quality,
        }
        points.append(point)

    return render_template("homepage.html", points=points)


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


@app.post("/sensor_data/<device_name>")
def process_sensor_data(device_name):

    json = request.get_json()

    db["Devices"].find_one({"device_name": device_name})
    if db["Devices"].count_documents({"device_name": device_name}) == 0:
        print(f"Device {device_name} not found in database")
        print("Adding device to database")
        db["Devices"].insert_one(
            {"device_name": device_name, "lat": json["lat"], "long": json["long"]}
        )
        print(f"Device {device_name} added to database")

    if "measurement_type" not in json:
        print("Missing type")
        return "Missing value", 400
    if "value" not in json:
        print("Missing value")
        return "Missing value", 400

    measurement_type = json["measurement_type"]
    if measurement_type not in valid_measurement_types:
        # Create response with 400 status code
        print(f"Invalid measurement type: {measurement_type}")
        return "Invalid measurement type", 400

    value = json["value"]
    process_data_response = process_data(device_name, measurement_type, value)
    print(f"process_data_response: {process_data_response}")
    # Create response with 200 status code
    return "OK"


@app.get("/sensor_data/<device_name>")
def show_sensor_data(device_name):
    if not USING_DB:
        return "No data available"

    data = []

    for measurement_type in valid_measurement_types:
        last_ten = list(
            db["Sensor Data"]
            .find({"measurement_type": measurement_type, "device_name": device_name})
            .sort("timestamp", -1)
            .limit(10)
        )

        values = [doc["sensor_value"] for doc in last_ten if "sensor_value" in doc]
        if values:
            average = sum(values) / len(values)
            data.append({"type": measurement_type, "value": round(average, 2)})
        else:
            print(f"No {measurement_type} data available")
            data.append({"type": measurement_type, "value": None})

    print("Averages:", data)
    return render_template("sensor_data.html", data=data)
