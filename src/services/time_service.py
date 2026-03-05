from datetime import time, date


def has_expired(
        current_date: date,
        current_time: time,
        expiration_date: date,
        expiration_time: time,
):
    if current_date < expiration_date:
        return False
    elif current_date == expiration_date:
        if current_time < expiration_time:
            return False
        else:
            return True
    return True

