from datetime import datetime
import time

def generate_datetime_now():
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return now

def generate_epoch_millis_now():
    now = round(time.time() * 1000)
    return now