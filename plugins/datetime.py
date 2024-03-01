# datetime.py
import pytz
from datetime import datetime
from plugins.format_types import format_types

def get_datetime(format_type):
    """
    Retrieves the current date and time in Kolkata timezone and formats it according to the specified format_type.

    Args:
        format_type (int): An integer representing the desired formatting style. Obtained from format_types.py.

    Returns:
        str: The formatted date and time string.

    Raises:
        ValueError: If an invalid format_type is provided.
    """

    # Set Kolkata timezone and get current datetime
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    return format_types(now, format_type)
