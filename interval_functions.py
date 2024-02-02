# interval_functions.py
import pytz
from datetime import datetime, timedelta

async def get_date_range(interval):
    today = datetime.now(pytz.timezone('Asia/Kolkata')).date()

    if interval == 'daily':
        start_date = datetime(today.year, today.month, today.day, tzinfo=pytz.timezone('Asia/Kolkata'))
        end_date = start_date + timedelta(days=1)
    elif interval == 'monthly':
        start_date = datetime(today.year, today.month, 1, tzinfo=pytz.timezone('Asia/Kolkata'))
        end_date = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(
            year=start_date.year + 1, month=1)
    elif interval == 'yearly':
        start_date = datetime(today.year, 1, 1, tzinfo=pytz.timezone('Asia/Kolkata'))
        end_date = start_date.replace(year=start_date.year + 1)
    else:
        raise ValueError("Invalid interval. Use 'daily', 'monthly', or 'yearly'.")

    return start_date, end_date
