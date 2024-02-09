import pytz
from datetime import datetime, timedelta
from format_types import get_format

def get_expiry_datetime(format_type, base_datetime=None, expiry_option=None):
    """
    Retrieves the current date and time (or a specified base datetime) in Kolkata timezone
    and formats it according to the given format_type, along with calculating and formatting
    the next expiry date/time based on the provided options.

    Args:
        format_type (int): An integer representing the desired formatting style.
        base_datetime (datetime, optional): The base datetime to calculate expiry from.
        expiry_option (str or int, optional): The expiry option to calculate.

    Returns:
        tuple: A tuple containing two elements:
            - formatted_datetime (str): The formatted expiry date and time.
            - expiry_option (str): The formatted expiry option.
    """

    # Set Kolkata timezone
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST) if not base_datetime else base_datetime

    
    expiry_options = [
        {f"now_to_{i}m": i for i in range(1, 1440)},
        {f"today_to_{i}d": i for i in range(1, 365)}
    ]

    # Calculate expiry date/time based on expiry_option
    expiry_datetime = None
    for option_dict in expiry_options:
        if expiry_option in option_dict:
            if expiry_option.startswith("now_to_"):
                delta_minutes = option_dict[expiry_option]
                expiry_datetime = now + timedelta(minutes=delta_minutes)
            elif expiry_option.startswith("today_to_"):
                delta_days = option_dict[expiry_option]
                expiry_datetime = now + timedelta(days=delta_days)
            break  # Break loop once option is found

    
    format_type = get_format(expiry_datetime, format_type)

    formatted_date = expiry_datetime.strftime(format_type) if expiry_datetime else None
    formatted_time = expiry_datetime.strftime(format_type) if expiry_datetime else None

    return formatted_date, formatted_time

def get_expiry_name(expiry_option):
    """
    Retrieves the name of the expiry date/time based on the expiry option.

    Args:
        expiry_option (str): The expiry option to get the name for.
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
        str: The name of the expiry date/time.
    """
    expiry_options = [
        {f"now_to_{i}m": i for i in range(1, 1440)},
        {f"today_to_{i}d": i for i in range(1, 365)}
    ]

    # Calculate expiry date/time based on expiry_option
    expiry_name = None
    for option_dict in expiry_options:
        if expiry_option in option_dict:
            if expiry_option.startswith("now_to_"):
                delta_minutes = int(expiry_option.split("_")[2][:-1])
                if delta_minutes == 5:
                    return "Next 5 minutes"
                elif delta_minutes == 10:
                    return "Next 10 minutes"
                elif delta_minutes == 15:
                    return "Next 15 minutes"
                elif delta_minutes == 20:
                    return "Next 20 minutes"
                elif delta_minutes == 30:
                    return "Next 30 minutes"
                elif delta_minutes == 45:
                    return "Next 45 minutes"
                elif delta_minutes == 60:
                    return "Next 60 minutes"
                else:
                    return f"Next {delta_minutes} Minutes"
            elif expiry_option.startswith("today_to_"):
                delta_days = int(expiry_option.split("_")[2][:-1])
                if delta_days == 1:
                    return "Tomorrow"
                elif delta_days == 7:
                    return "Next week"
                elif delta_days == 28 or delta_days == 30:
                    return "Next month"
                elif delta_days == 60:
                    return "Next 2 months"
                elif delta_days == 90:
                    return "Next quarter"
                elif delta_days == 180:
                    return "Next 6 months"
                elif delta_days == 365:
                    return "Next year"
                else:
                    return f"Next {delta_days} days"
            break  # Break loop once option is found
    return expiry_name
    
