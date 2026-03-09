from datetime import datetime


def has_expired(
        current_datetime: datetime,
        expiration_datetime: datetime
):
    if current_datetime < expiration_datetime:
        return False
    else:
        return True

