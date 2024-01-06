from flask import Flask, render_template, Response, jsonify
from datetime import datetime, timedelta
import time
import websocket
import json
import joblib
import numpy as np
import math
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
kline_data_1m = None
data=None
model_1m = joblib.load('Model_1m.joblib')
def get_nearest_multiple_of_1():
    current_time = datetime.utcnow()
    next_minute = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    remaining_seconds = int((next_minute - current_time).total_seconds())
    return remaining_seconds
def utc_countdown_nearest_multiple_of_1():
    remaining_seconds = get_nearest_multiple_of_1()
    counter_data = {"counter": remaining_seconds-2}
    with open('time.json', 'w') as file:
        json.dump(counter_data, file)

@app.route("/stream1m")
def data():
    utc_countdown_nearest_multiple_of_1()
    def Five_Minute_Function():
        symbol = "btcusdt"
        interval = "1m"
        with open('time.json', 'r') as file:
            counter=json.load(file)

        def on_message(ws_app, message):
            global kline_data_1m,data
            data = json.loads(message)
            ws_app.close()
        def on_error(_, error):
            print(f"WebSocket Error: {error}")
        def on_close(_, close_status_code, close_msg):
            print("WebSocket Closed")
        def on_open(ws_app):
            print('WebSocket opened')
        def predict():
            global data
            open_val = float(f"{float(data['k']['o']):.2f}")
            high_val = float(f"{float(data['k']['h']):.2f}")
            low_val = float(f"{float(data['k']['l']):.2f}")
            volume_val = float(f"{float(data['k']['v']):.2f}")
            values = [open_val, high_val, low_val, volume_val]
            arr = [np.array(values)]
            prediction_1m = model_1m.predict(arr)
            kline_data_1m = prediction_1m
            print(kline_data_1m)
            return str(float(kline_data_1m))
        websocket_url = 'wss://stream.binance.com:9443/ws/' + symbol + '@kline_' + interval
        ws_app = websocket.WebSocketApp(websocket_url, on_open=on_open, on_message=on_message, on_error=on_error,
                                       on_close=on_close)
        ws_app.run_forever()
        while counter['counter'] >= 0:
            minutes, seconds = divmod(counter['counter'], 60)
            formatted_time = f"{minutes:02d}:{seconds:02d}"
            counter['time']=formatted_time
            with open('time.json', 'w') as file:
                json.dump(counter, file)  
            if counter['counter'] == 0:
                predict_data = predict()
                print(predict_data)
                with open('output.json', 'w') as file:
                    json.dump(predict_data, file)   
                yield (f"data:{predict_data}-{counter['time']}\n\n")
                counter['counter'] = 60
                with open('time.json','w') as file:
                    json.dump(counter,file)
            else:
                with open('output.json', 'r') as file:
                    prediction = json.load(file)
                yield (f"data:{prediction}-{counter['time']}\n\n")
            time.sleep(1)
            counter['counter']  -= 1
            with open('time.json','w') as file:
                json.dump(counter,file)
    return Response(Five_Minute_Function(), content_type="text/event-stream")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True,port=5000)
