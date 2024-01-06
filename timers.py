import time
from datetime import datetime, timedelta

def get_nearest_multiple_of_1():
    current_time = datetime.utcnow()
    next_minute = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    remaining_seconds = int((next_minute - current_time).total_seconds())
    return remaining_seconds
def utc_countdown_nearest_multiple_of_1():
    while True:
        remaining_seconds = get_nearest_multiple_of_1()
        counter_data = {"counter": remaining_seconds-3}
        print(remaining_seconds,end='\r')

utc_countdown_nearest_multiple_of_1()        