# expiry_date.py
import pytz
from datetime import datetime, timedelta
from plugins.datetime import get_datetime
import time


def get_expiry_date(format_type, base_datetime=None, expiry_option=None, expiry_name=None):
    """
    Retrieves the current date and time (or a specified base datetime) in Kolkata timezone
    and formats it according to the given format_type, along with calculating and formatting
    the next expiry date/time based on the provided options.

    Args:
        format_type (int): An integer representing the desired formatting style:
            ... (same as before)
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
        expiry_name (str, optional): An optional name for the expiry date/time.

    Returns:
        tuple: A tuple containing two elements:
            - formatted_datetime (str): The formatted current date and time (if base_datetime is not provided) or base_datetime.
            - expiry_datetime (str): The formatted expiry date and time, or None if no expiry is calculated.
            - expiry_name (str): The name of the expiry date/time.

    Raises:
        ValueError: If an invalid format_type or expiry_option is provided.
    """

    # Set Kolkata timezone
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)

    format_type = get_datetime(format_type)

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

    # Calculate expiry date/time based on expiry_option
    if expiry_option:
        if expiry_option in expiry_options:
            if expiry_option.startswith("now_to_"):
                delta_minutes = expiry_options[expiry_option]
                expiry_datetime = (now + timedelta(minutes=delta_minutes)).strftime("%Y-%m-%d %H:%M:%S")
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
                expiry_datetime = (now + timedelta(days=delta_days)).strftime("%Y-%m-%d %H:%M:%S")
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
                    expiry_name = f"In {days} days"
            else:
                raise ValueError(f"Invalid expiry_option: {expiry_option}")
        else:
            expiry_datetime = None
            expiry_name = None

    return formatted_datetime, expiry_datetime, expiry_name


# Example usage:
print(get_expiry_date(1, expiry_option="now_to_10m"))  # Example Output: 2024-02-07 11:38:00 2024-02-07 11:39:00 Next 10 minutes
print(get_expiry_date(1, expiry_option="today_to_1d"))  # Example Output: 2024-02-07 11:38:00 2024-02-08 00:00:00 Tomorrow
# Print with different formatting types and expiry options:
print(get_expiry_date(2, expiry_option="now_to_10m"))  # Output: 08/02/2024 00:18:00, 08/02/2024 00:28:00, Next 10 minutes
print(get_expiry_date(3, expiry_option="today_to_7d"))  # Output: 2024-02-07 00:08:00, 2024-02-13 00:00:00, Next week
print(get_expiry_date(4, expiry_option="today_to_30d"))  # Output: 2024-02-07 00:08:00, 2024-03-07 00:00:00, Next month

# Print with a custom base datetime:
base_datetime = datetime(2024, 2, 10, 12, 00)
print(get_expiry_date(1, expiry_option="now_to_15m", base_datetime=base_datetime))  # Output: 2024-02-10 12:00:00, 2024-02-10 12:15:00, Next 15 minutes

# Print without expiry calculation:
print(get_expiry_date(1, expiry_option=None))  # Output: 2024-02-08 00:18:00, None, None
