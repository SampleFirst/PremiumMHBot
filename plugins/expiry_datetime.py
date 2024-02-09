# expiry_date.py
import pytz
from datetime import datetime, timedelta
from plugins.datetime import get_datetime
import time


def get_expiry_datetime(format_type, base_datetime=None, expiry_option=None, expiry_name=""):
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
    now = datetime.now(IST) if not base_datetime else base_datetime

    format_type = get_datetime(format_type)

    expiry_options = {
        {f"now_to_{i}m": i for i in range(1, 1440)},
        {f"today_to_{i}d": i for i in range(1, 365)}
    }

    # Calculate expiry date/time based on expiry_option
    if expiry_option:
        if expiry_option in expiry_options:
            if expiry_option.startswith("now_to_"):
                delta_minutes = expiry_options[expiry_option]
                expiry_datetime = now + timedelta(minutes=delta_minutes)
                expiry_date = expiry_datetime.strftime(format_type)
                expiry_time = expiry_datetime.strftime(format_type)
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
                    expiry_name = f"Next {delta_minutes} Minutes"
            elif expiry_option.startswith("today_to_"):
                delta_days = expiry_options[expiry_option]
                expiry_datetime = now + timedelta(days=delta_days)
                expiry_date = expiry_datetime.strftime(format_type)
                expiry_time = expiry_datetime.strftime(format_type)
                if delta_days == 1:
                    expiry_name = "Tomorrow"
                elif delta_days == 7:
                    expiry_name = "Next week"
                elif delta_days == 28:
                    expiry_name = "Next month"
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
                    expiry_name = f"Next {delta_days} days"
            else:
                raise ValueError(f"Invalid expiry_option: {expiry_option}")
        else:
            expiry_date = None
            expiry_time = None
            expiry_name = None

    return base_datetime, expiry_date, expiry_time, expiry_name
    
    
    
# Example Output 
format_type = "%Y-%m-%d %H:%M:%S"

# Example 1: Calculate expiry date/time for next 10 minutes
expiry_option = "now_to_10m"
base_datetime = datetime.now()
base_datetime, base_date, base_time, expiry_date, expiry_time, expiry_name = get_expiry_datetime(format_type=1, base_datetime, expiry_option)

print("Example 1:")
print("Base datetime:", base_datetime)
print("Base date:", base_date)
print("Base time:", base_time)
print("Expiry date:", expiry_date)
print("Expiry time:", expiry_time)
print("Expiry name:", expiry_name)
print()

# Example 2: Calculate expiry date/time for Next Month 
expiry_option = "today_to_30d"
base_datetime = datetime.now()
base_datetime, base_date, base_time, expiry_date, expiry_time, expiry_name = get_expiry_datetime(format_type=1, base_datetime, expiry_option)

print("Example 2:")
print("Base datetime:", base_datetime)
print("Base date:", base_date)
print("Base time:", base_time)
print("Expiry date:", expiry_date)
print("Expiry time:", expiry_time)
print("Expiry name:", expiry_name)
print()
