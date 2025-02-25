from flask import Flask, request, jsonify
import requests
app = Flask(__name__)

##################PY MONGO##################
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://dbBernard:gunhouse147@cluster0.fril3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client['MyDB']
my_collenction = db['SensorData']

def store_data(data):
    result = my_collenction.insert_one(data)
    print(result.inserted_id)

def get_data():
    get_result = my_collenction.find()
    return get_result

def get_last_data():
    last_data = my_collenction.find().sort("_id", -1).limit(1) 
    return list(last_data)[0] if last_data else None

def send_to_ubidots(data):
    UBIDOTS_TOKEN = "BBUS-FAxUKR2qeru7TKv6hyJyuPkBqLE6hH" 
    DEVICE_LABEL = "assg_2_siao-langs"  
    UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/assg_2_siao-langs/"

    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "temperature": data["temperature"],
        "humidity": data["humidity"]
    }

    try:
        response = requests.post(UBIDOTS_URL, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            print("Data sent to Ubidots successfully:", response.json())
        else:
            print("Failed to send data to Ubidots:", response.text)
    except Exception as e:
        print("Error sending to Ubidots:", e)
###############################################

list_temp = []

@app.route('/')
def entry_point():
    return jsonify(message="Hello World!")

@app.route('/test', methods=['POST', 'GET'])
def salam_sehat():
    if request.method == 'POST':
        body = request.get_json()
        
        if not body or 'data' not in body:
            return jsonify(error="Invalid JSON body, 'data' key required"), 400
        
        params = request.args.get('params', 'default_value')  # Default jika tidak ada params
        return jsonify(message="Salam POST untuk kita semua", data=body['data'], params=params)
    
    elif request.method == 'GET':
        return jsonify(message="Salam GET untuk kita semua")

# @app.route('/sensor1', methods=['POST'])
# def simpan_data_sensor():
#     # print("Get")
#     if request.method == 'POST':
#         body = request.get_json()
#         temperature = body['temperature']
#         humidity = body['humidity']
#         timestamp = body['timestamp']
#         list_temp.append({
#             "temperature":temperature,
#             "humidity":humidity,
#             "timestamp":timestamp
#         })

#         print(list_temp)

#         return{
#             "massage" : "Hello, i have proccesed your req"
#         }
    
#     elif request.method == 'GET':
#         return jsonify(message="Salam GET untuk kita semua")

@app.route('/sensor1', methods=['POST', 'GET'])
def simpan_data_sensor():
    if request.method == 'POST':
        body = request.get_json()

        if not body:
            return jsonify({"error": "Invalid JSON"}), 400 

        try:
            temperature = body.get('temperature')
            humidity = body.get('humidity')
            timestamp = body.get('timestamp')

            if temperature is None or humidity is None or timestamp is None:
                return jsonify({"error": "Missing required fields"}), 400

            data = {
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": timestamp
            }

            list_temp.append({
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": timestamp
            })

            print(list_temp)

            store_data(data)

            last_data = get_last_data()
            if last_data:
                send_to_ubidots(last_data)

            return jsonify({"message": "Data stored and sent to Ubidots"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'GET':
        try:
            data = list(my_collenction.find({}, {"_id": 0}))
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)

# @app.route('/sensor1', methods=['POST'])
# def simpan_data_sensor():
#     """ Endpoint untuk menyimpan data sensor ke database """
#     body = request.get_json()

#     
#     if not body or 'temperature' not in body or 'humidity' not in body or 'timestamp' not in body:
#         return jsonify(error="Invalid JSON body. Required fields: temperature, humidity, timestamp"), 400

#     
#     temperature = body['temperature']
#     humidity = body['humidity']
#     timestamp = body['timestamp']

#     
#     sensor_data = {
#         "temperature": temperature,
#         "humidity": humidity,
#         "timestamp": timestamp
#     }

#    
#     inserted_id = store_data(sensor_data)

#     return jsonify(
#         message="Data sensor berhasil disimpan ke database",
#         inserted_id=inserted_id
#     )

# @app.route('/sensor1/temperature/avg', methods=['GET'])
# def get_rata2_suhu():
#     print(list_temp)
#     if not list_temp:
#         return jsonify({"error" : "theres no temp data"})

#     total_suhu = sum(data["temperature"] for data in list_temp)
#     avg_suhu = total_suhu/len(list_temp)

#     return jsonify({"average_temp" : avg_suhu})

# @app.route('/sensor1/temperature/avg', methods=['GET'])
# def get_rata2_suhu():
#     """ Endpoint untuk menghitung rata-rata suhu dari database """
#     all_data = list(my_collenction.find({}, {"_id": 0, "temperature": 1}))

#     if not all_data:
#         return jsonify({"error": "Tidak ada data suhu yang tersedia"}), 404

#     total_suhu = sum(data["temperature"] for data in all_data)
#     avg_suhu = total_suhu / len(all_data)

#     return jsonify({"average_temp": avg_suhu})

# @app.route('/sensor1/humidity/avg', methods=['GET'])
# def get_rata2_kelembapan():
#     all_hum_data = list(my_collenction.find({}, {"_id": 0, "humidity":1}))

#     if not all_hum_data:
#         return jsonify({"error": "Tidak ada data kelembapan yang tersedia"}), 404

#     total_kelembapan = sum(data["humidity"] for data in all_hum_data)
#     avg_kelembapan = total_kelembapan/len(all_hum_data)

#     return jsonify({"Average hum" : avg_kelembapan})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0',debug=True, port=7000)