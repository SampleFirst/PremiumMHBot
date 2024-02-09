import pytz
from datetime import datetime, timedelta
from plugins.datetime import get_datetime  # Assume this function gets a valid format type

def get_expiry_datetime(format_type, base_datetime=None, expiry_option=None):
    """
    Retrieves the current date and time (or a specified base datetime) in Kolkata timezone
    and formats it according to the given format_type, along with calculating and formatting
    the next expiry date/time based on the provided expiry_option.

    Args:
        format_type (int): An integer representing the desired formatting style from plugins.datetime.
        base_datetime (datetime, optional): The base datetime to use instead of now.
        expiry_option (str or int, optional): The expiry option to calculate:
            - "now_to_5m": Next 5 minutes
            - "now_to_10m": Next 10 minutes
            - "now_to_15m": Next 15 minutes
            - "now_to_20m": Next 20 minutes
            - "now_to_30m": Next 30 minutes
            - "now_to_45m": Next 45 minutes
            - "now_to_60m": Next 60 minutes
            - "today_to_1d": Tomorrow
            - "today_to_7d": Next week
            - "today_to_30d": Next month
            - "today_to_60d": Next 2 months
            - "today_to_90d": Next quarter
            - "today_to_180d": Next 6 months
            - "today_to_365d": Next year
            - None: No expiry calculation is performed.

    Returns:
        tuple: A tuple containing three elements:
            - formatted_datetime (str): The formatted current date and time.
            - expiry_datetime (str or None): The formatted expiry date and time, or None if no expiry is calculated.
            - expiry_name (str or None): The name of the expiry date/time, or None if no expiry is calculated.

    Raises:
        ValueError: If an invalid format_type or expiry_option is provided.
    """

    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST) if base_datetime is None else base_datetime

    format_type = get_datetime(format_type)  # Retrieve valid format string

    expiry_options = {
        "now_to_5": 5,
        "now_to_10": 10,
        "now_to_15": 15,
        "now_to_20": 20,
        "now_to_30": 30,
        "now_to_45": 45,
        "now_to_60": 60,
        "today_to_1d": 1,
        "today_to_7d": 7,
        "today_to_30d": 30,
        "today_to_60d": 60,
        "today_to_90d": 90,
        "today_to_180d": 180,
        "today_to_365d": 365,
    }

    if expiry_option:
        if expiry_option in expiry_options:
            if expiry_option.startswith("now_to_"):
                delta_minutes = expiry_options[expiry_option]
                expiry_datetime = (now + timedelta(minutes=delta_minutes)).strftime(format_type)
                if delta_minutes == 5:
                    expiry_name = "Next 5 minutes"
                elif delta_minutes == 10:
                    expiry_name = "Next 10 minutes"
                elif delta_minutes == 15:
                    expiry_name = "Next 15 minutes"
                elif delta_minutes == 20:
                    expiry_name = "Next 20 minutes"
                elif delta_minutes == 30:
                    expiry_name = "Next 30 minutes"
                elif delta_minutes == 45:
                    expiry_name = "Next 45 minutes"
                elif delta_minutes == 60:
                    expiry_name = "Next 60 minutes"
                else:
                    expiry_name = f"In {minutes} Minutes"
            elif expiry_option.startswith("today_to_"):
                delta_days = expiry_options[expiry_option]
                expiry_datetime = (now + timedelta(days=delta_days)).strftime(format_type)
                if delta_days == 1:
                    expiry_name = "Tomorrow"
                elif delta_days == 7:
                    expiry_name = "Next week"
                elif delta_days == 30:
                    expiry_name = "Next month"
                elif delta_days == 60:
                    expiry_name = "Next 2 months"
                elif delta_days == 90:
                    expiry_name = "Next quarter"
                elif delta_days == 180:
                    expiry_name = "Next 6 months"
                elif delta_days == 365:
                    expiry_name = "Next year"
                else:
                    expiry_name = f"In {delta_days} days"
            else:
                raise ValueError(f"Invalid expiry_option: {expiry_option}")
        else:
            expiry_datetime = None
            expiry_name = None
    else:
        expiry_datetime = None
        expiry_name = None

    return format_type, expiry_datetime, expiry_name


# Usage example (assuming get_datetime returns valid formats):
expiry_date = get_expiry_datetime(1)
expiry_time = get_expiry_datetime(3)
expiry_name = get_expiry_datetime(1, expiry_option="today_to_30d")

print(f"Expiry date: {expiry_date}")
print(f"Expiry time: {expiry_time}")
print(f"Expiry name: {expiry_name}")

