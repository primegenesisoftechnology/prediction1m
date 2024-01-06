import time
from datetime import datetime

def live_utc_clock():
    while True:
        current_utc_time = datetime.utcnow()
        minutes, seconds = current_utc_time.minute, current_utc_time.second
        print(f"UTC Time:{minutes:02d}:{seconds:02d}", end='\r')
        time.sleep(1)

if __name__ == "__main__":
    live_utc_clock()
