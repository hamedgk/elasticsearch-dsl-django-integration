from datetime import datetime
import time

def generate_datetime_now():
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return now

def generate_epoch_millis_now():
    now = round(time.time() * 1000)
    return now

def is_iso_datetime(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False

def is_epoch_millis(timestamp_string):
    try:
        timestamp = int(timestamp_string)
        datetime.fromtimestamp(timestamp / 1000)
        return True
    except (ValueError, OverflowError):
        return False

def is_valid_datetime(input):
        return is_epoch_millis(input) or is_iso_datetime(input)