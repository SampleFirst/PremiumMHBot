# format_types.py

def get_format(expiry_datetime, format_type):
    """
    Formats the expiry datetime according to the given format_type.

    Args:
        expiry_datetime (datetime): The expiry datetime object.
        format_type (int): An integer representing the desired formatting style.

    Returns:
        str: The formatted expiry datetime string.
    """
    if format_type == 1:
        return expiry_datetime.strftime("%d %B %Y")  # Day number, month text name, year number
    elif format_type == 2:
        return expiry_datetime.strftime("%d/%m/%Y")  # Day/month/year
    elif format_type == 3:
        return expiry_datetime.strftime("%I:%M %p")  # Hour minute AM/PM
    elif format_type == 4:
        return expiry_datetime.strftime("%I:%M:%S %p")  # Hour minute second AM/PM
    elif format_type == 5:
        return expiry_datetime.strftime("%I:%M:%S")  # Hour minute second (12 hours)
    elif format_type == 6:
        return expiry_datetime.strftime("%H:%M:%S")  # Hour minute second (24 hours)
    elif format_type == 7:
        return expiry_datetime.strftime("%Y-%m-%d")  # Year-month-day
    elif format_type == 8:
        return expiry_datetime.strftime("%m-%d-%Y")  # Month-day-year
    elif format_type == 9:
        return expiry_datetime.strftime("%d %b")  # Day-month
    elif format_type == 10:
        return expiry_datetime.strftime("%b %d")  # Month day
    elif format_type == 11:
        return expiry_datetime.strftime("%A")  # Day of the week
    elif format_type == 12:
        return str(expiry_datetime.isocalendar()[1])  # Week number
    elif format_type == 13:
        return expiry_datetime.isoformat()  # ISO 8601 date and time
    else:
        raise ValueError("Invalid format_type. Please choose a number between 1 and 13.")
