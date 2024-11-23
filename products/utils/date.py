from datetime import datetime
from elasticsearch_dsl import Date
import time

def generate_datetime_now():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now

def generate_date_now():
    now = datetime.now().strftime("%Y-%m-%d")
    return now

def generate_epoch_millis_now():
    now = round(time.time() * 1000)
    return now

def is_datetime_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def is_date_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
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
        return is_epoch_millis(input) or is_date_format(input) or is_datetime_format(input)


class VariantFormatDate(Date):
        def _deserialize(self, data):
                if isinstance(data, str):
                        try:
                                # Handle hardcoded format yyyy-MM-dd HH:mm:ss
                                if " " in data:
                                        return datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                                # Handle ISO-8601 flexible datetime (strict_date_optional_time)
                                return datetime.fromisoformat(data)
                        except ValueError as e:
                                raise ValidationException(
                                f"Could not parse date from the value ({data!r}) using specified formats", e
                                )

                if isinstance(data, int):
                        try:
                                # Handle Unix epoch milliseconds
                                if data > 1e12:  # epoch_millis
                                        return datetime.utcfromtimestamp(data / 1000.0)
                                        raise ValidationException(
                                        f"Value ({data!r}) is not valid for epoch_millis (too small)"
                                        )
                        except ValueError as e:
                                raise ValidationException(
                                f"Could not parse timestamp from the value ({data!r})", e
                                )

                if isinstance(data, datetime):
                        if self._default_timezone and data.tzinfo is None:
                                data = data.replace(tzinfo=self._default_timezone)
                        return data
                if isinstance(data, date):
                        return data

                raise ValidationException(f"Could not parse date from the value ({data!r})")

