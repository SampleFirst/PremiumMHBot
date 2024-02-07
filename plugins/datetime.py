# datetime.py
import pytz
from datetime import datetime

def get_datatime(format_type):
    """
    Retrieves the current date and time in Kolkata timezone and formats it according to the specified format_type.

    Args:
        format_type (int): An integer representing the desired formatting style:
            1: Day number, month text name, year number (e.g., 1 January 2024)
            2: Day/month/year (e.g., 1/1/2024)
            3: Hour minute AM/PM (e.g., 12:25 AM)
            4: Hour minute second AM/PM (e.g., 12:25:23 AM)
            5: Hour minute second (12 hours) (e.g., 12:25:23)
            6: Hour minute second (24 hours) (e.g., 00:25:23)
            7: Year-month-day (e.g., 2024-02-08)
            8: Month-day-year (e.g., 02-08-2024)
            9: Day-month (e.g., 08 Feb)
            10: Month day (e.g., Feb 8)
            11: Day of the week (e.g., Wednesday)
            12: Week number (e.g., 6)
            13: ISO 8601 date and time (e.g., 2024-02-08T03:57:10+05:30)

    Returns:
        str: The formatted date and time string.

    Raises:
        ValueError: If an invalid format_type is provided.
    """

    # Set Kolkata timezone and get current datetime
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    if format_type == 1:
        return now.strftime("%d %B %Y")  # Day number, month text name, year number
    elif format_type == 2:
        return now.strftime("%d/%m/%Y")  # Day/month/year
    elif format_type == 3:
        return now.strftime("%I:%M %p")  # Hour minute AM/PM
    elif format_type == 4:
        return now.strftime("%I:%M:%S %p")  # Hour minute second AM/PM
    elif format_type == 5:
        return now.strftime("%H:%M:%S")  # Hour minute second (12 hours)
    elif format_type == 6:
        return now.strftime("%H:%M:%S")  # Hour minute second (24 hours)
    elif format_type == 7:
        return now.strftime("%Y-%m-%d")  # Year-month-day
    elif format_type == 8:
        return now.strftime("%m-%d-%Y")  # Month-day-year
    elif format_type == 9:
        return now.strftime("%d %b")  # Day-month
    elif format_type == 10:
        return now.strftime("%b %d")  # Month day
    elif format_type == 11:
        return now.strftime("%A")  # Day of the week
    elif format_type == 12:
        return str(now.isocalendar()[1])  # Week number
    elif format_type == 13:
        return now.isoformat()  # ISO 8601 date and time
    else:
        raise ValueError("Invalid format_type. Please choose a number between 1 and 13.")

# Example usage:
print(get_datatime(1))  # Output: 8 February 2024
print(get_datatime(3))  # Output: 03:57 AM
print(get_datatime(6))  # Output: 03:57:10
print(get_datatime(7))  # Output:
