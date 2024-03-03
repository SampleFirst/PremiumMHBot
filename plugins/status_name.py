# status_name.py

def status_name(status_num):
    if status_num == 1:
        return status_text("is Attempt")
    elif status_num == 2:
        return status_text("is Confirm")
    elif status_num == 3:
        return status_text("is Premium")
    elif status_num == 4:
        return status_text("Attempt Cancel")
    elif status_num == 5:
        return status_text("Confirm Cancel")
    elif status_num == 6:
        return status_text("Premium Cancel")
    elif status_num == 7:
        return status_text("Attempt Remove")
    elif status_num == 8:
        return status_text("Confirm Remove")
    elif status_num == 9:
        return status_text("Premium Remove")
    else:
        raise ValueError("Invalid status_num. Please choose a number between 1 and 9.")
