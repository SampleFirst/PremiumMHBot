# format_types.py
from datetime import datetime

def format_types(obj, format_type):
    """
    Formats the datetime object according to the given format_type.

    Args:
        obj (datetime): The datetime object to be formatted.
        format_type (int): An integer representing the desired formatting style.

    Returns:
        str: The formatted datetime string.
    """
    if format_type == 1:
        return obj.strftime("%d %B %Y")  # Day number, month text name, year number
    elif format_type == 2:
        return obj.strftime("%d/%m/%Y")  # Day/month/year
    elif format_type == 3:
        return obj.strftime("%I:%M %p")  # Hour minute AM/PM
    elif format_type == 4:
        return obj.strftime("%I:%M:%S %p")  # Hour minute second AM/PM
    elif format_type == 5:
        return obj.strftime("%I:%M:%S")  # Hour minute second (12 hours)
    elif format_type == 6:
        return obj.strftime("%H:%M:%S")  # Hour minute second (24 hours)
    elif format_type == 7:
        return obj.strftime("%Y-%m-%d")  # Year-month-day
    elif format_type == 8:
        return obj.strftime("%m-%d-%Y")  # Month-day-year
    elif format_type == 9:
        return obj.strftime("%d %b")  # Day-month
    elif format_type == 10:
        return obj.strftime("%b %d")  # Month day
    elif format_type == 11:
        return obj.strftime("%A")  # Day of the week
    elif format_type == 12:
        return str(obj.isocalendar()[1])  # Week number
    elif format_type == 13:
        return obj.isoformat()  # ISO 8601 date and time
    elif format_type == 14:
        return obj.strftime("%d %B %Y %H:%M:%S")  # Day month year hour minute second
    elif format_type == 15:
        return obj.strftime("%m-%d-%Y %I:%M:%S %p")  # Month-day-year hour minute second AM/PM
    elif format_type == 16:
        return obj.strftime("%d/%m/%Y %I:%M:%S %p")  # Day/month/year hour minute second AM/PM
    elif format_type == 17:
        return obj.strftime("%A, %d %B %Y")  # Day of the week, day month year
    elif format_type == 18:
        return obj.strftime("%Y-%m-%d %H:%M:%S")  # Year-month-day hour minute second
    elif format_type == 19:
        return obj.strftime("%Y-%m-%d %I:%M:%S %p")  # Year-month-day hour minute second AM/PM
    elif format_type == 20:
        return obj.strftime("%B %d, %Y %I:%M:%S %p")  # Month day, year hour minute second AM/PM
    elif format_type == 21:
        return obj.strftime("%Y-%m-%d %H:%M:%S")  # Updated format
    else:
        raise ValueError("Invalid format_type. Please choose a number between 1 and 21.")

