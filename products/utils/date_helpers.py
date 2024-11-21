from datetime import datetime

def format_to_datetime_string(value):
    """
    Converts a datetime object or epoch milliseconds to 'yyyy-MM-dd HH:mm:ss' format.
    """
    if isinstance(value, int):  # Assume epoch millis
        dt = datetime.utcfromtimestamp(value / 1000.0)
    elif isinstance(value, datetime):
        dt = value
    else:
        raise ValueError("Unsupported value type. Expected datetime or epoch milliseconds.")
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_to_epoch_millis(value):
    """
    Converts a datetime object or a 'yyyy-MM-dd HH:mm:ss' string to epoch milliseconds.
    """
    if isinstance(value, str):  # Assume string format 'yyyy-MM-dd HH:mm:ss'
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    elif isinstance(value, datetime):
        dt = value
    else:
        raise ValueError("Unsupported value type. Expected datetime or formatted string.")
    
    return int(dt.timestamp() * 1000)

def parse_iso_to_datetime(value):
    """
    Converts an ISO 8601 string to a datetime object.
    """
    if not isinstance(value, str):
        raise ValueError("Unsupported value type. Expected ISO 8601 string.")
    
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def generate_datetime_now():
    """
    Generates the current datetime in 'yyyy-MM-dd HH:mm:ss' format.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now

def generate_epoch_millis_now():
    """
    Generates the current epoch time in milliseconds.
    """
    now = int(datetime.now().timestamp()*100)
    return now

def generate_combined_formats_now():
    """
    Generates both 'yyyy-MM-dd HH:mm:ss' and epoch millis for the current datetime.
    """
    now = datetime.utcnow()
    return {
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        "epoch_millis": int(now.timestamp() * 1000),
    }
