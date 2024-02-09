import pytz
from datetime import datetime, timedelta
from plugins.datetime import get_datetime


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

    format_type = get_datetime(format_type)

    expiry_options = [
        {f"now_to_{i}m": i for i in range(1, 1440)},
        {f"today_to_{i}d": i for i in range(1, 365)}
    ]

    # Calculate expiry date/time based on expiry_option
    if expiry_option:
        if expiry_option in expiry_options:
            if expiry_option.startswith("now_to_"):
                delta_minutes = expiry_options[expiry_option]
                expiry_datetime = now + timedelta(minutes=delta_minutes)
            elif expiry_option.startswith("today_to_"):
                delta_days = expiry_options[expiry_option]
                expiry_datetime = now + timedelta(days=delta_days)
            else:
                raise ValueError(f"Invalid expiry_option: {expiry_option}")
        else:
            expiry_datetime = None

    formatted_datetime = expiry_datetime.strftime(format_type) if expiry_datetime else None
    return formatted_datetime, expiry_option


def get_expiry_name(expiry_option):
    """
    Retrieves the name of the expiry date/time based on the expiry option.

    Args:
        expiry_option (str): The expiry option to get the name for.

    Returns:
        str: The name of the expiry date/time.
    """
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
    else:
        return None
