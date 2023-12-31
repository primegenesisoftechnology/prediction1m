from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import websocket
import json
import joblib
import numpy as np
import gzip
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
kline_data_1m=None
model_1m = joblib.load('Model_1m.joblib')
@socketio.on('connect')
def Live_stream():
    def One_Minute_Function():
        symbol = "btcusdt" 
        interval ="1m"
        def on_message(ws_app, message):
            global kline_data_1m
            data = json.loads(message)
            open_val = float(f"{float(data['k']['o']): .2f}")
            high_val = float(f"{float(data['k']['h']): .2f}")
            low_val = float(f"{float(data['k']['l']): .2f}")
            volume_val = float(f"{float(data['k']['v']): .2f}")
            values = [open_val, high_val, low_val, volume_val]
            arr = [np.array(values)]
            prediction_1m=model_1m.predict(arr)  
            kline_data_1m={"predict": prediction_1m.tolist()}
            ws_app.close()
        def on_error(_, error):
            print(f"WebSocket Error: {error}")
        def on_close(_, close_status_code, close_msg):
            print("WebSocket Closed")
        def on_open(ws_app):
            print('WebSocket opened')
        websocket_url = 'wss://stream.binance.com:9443/ws/' + symbol + '@kline_' + interval
        ws_app = websocket.WebSocketApp(websocket_url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        ws_app.run_forever()
        while True:
            socketio.emit('data_1m', {'message': kline_data_1m})
            # time.sleep(1) 
    One_Minute_Thread = threading.Thread(target=One_Minute_Function) 
    One_Minute_Thread.start()
    
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app, debug=True)
