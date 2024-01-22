from datetime import timedelta, date, datetime
import time
import pytz

def add_date():
    today = date.today()
    tz = pytz.timezone('Asia/Kolkata')
    curr_date = datetime.now(tz)
    
    formatted_date = curr_date.strftime('%Y-%m-%d')
    return formatted_date

def check_date():
    today = date.today()
    ex_date = today + timedelta(days=30)
    pattern = '%Y-%m-%d'
    epoch_time = int(time.mktime(time.strptime(str(ex_date), pattern)))
    normal_date = datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d')
    return epoch_time, normal_date

def check_expiry(saved_date):
    today = date.today()
    pattern = '%Y-%m-%d'
    epoch_today = int(time.mktime(time.strptime(str(today), pattern)))
    remaining_days = saved_date - epoch_today
    print(remaining_days)
    
    return remaining_days > 0

# Example usage:
# saved_date = check_date()[0]
# print(check_expiry(saved_date))
