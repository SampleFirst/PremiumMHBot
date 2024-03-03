# status_name.py

def get_status_name(status_num):
    if status_num == 1:
        return "is Attempt"
    elif status_num == 2:
        return "is Confirm"
    elif status_num == 3:
        return "is Premium"
    elif status_num == 4:
        return "Attempt Cancel"
    elif status_num == 5:
        return "Confirm Cancel"
    elif status_num == 6:
        return "Premium Cancel"
    elif status_num == 7:
        return "Attempt Remove"
    elif status_num == 8:
        return "Confirm Remove"
    elif status_num == 9:
        return "Premium Remove"
    else:
        raise ValueError("Invalid status_num. Please choose a number between 1 and 9.")

# Examples of using the corrected function:
print(get_status_name(1))  # Output: "is Attempt"
print(get_status_name(5))  # Output: "Confirm Cancel"
print(get_status_name(9))  # Output: "Premium Remove"
