# status_name.py

def get_status_name(status_num):
    if status_num == 1:
        return get_status_name("is Attempt")
    elif status_num == 2:
        return get_status_name("is Confirm")
    elif status_num == 3:
        return get_status_name("is Premium")
    elif status_num == 4:
        return get_status_name("Attempt Cancel")
    elif status_num == 5:
        return get_status_name("Confirm Cancel")
    elif status_num == 6:
        return get_status_name("Premium Cancel")
    elif status_num == 7:
        return get_status_name("Attempt Remove")
    elif status_num == 8:
        return get_status_name("Confirm Remove")
    elif status_num == 9:
        return get_status_name("Premium Remove")
    else:
        raise ValueError("Invalid status_num. Please choose a number between 1 and 9.")
