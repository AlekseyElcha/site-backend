# from datetime import datetime, date, time


def has_expired(
        current_datetime: datetime,
        expiration_datetime: datetime
):
    if current_datetime < expiration_datetime:
        return False
    else:
        return True


#
# def change_utc_into_local_tz(
#     utc_datetime: datetime,
#     local_tz: str,
# ) -> str:
#     local_timezone = pytz.timezone(local_tz)
#     local_datetime_str = str(utc_datetime.astimezone(local_timezone))[:-6]
#     return local_datetime_str
#
#
# def change_utc_date_and_time_into_local_tz(
#         utc_date: date,
#         utc_time: time,
#         local_tz: str,
# ) -> str:
#     local_timezone = pytz.timezone(local_tz)
#     utc_datetime = datetime.combine(utc_date, utc_time)
#     local_datetime_str = utc_datetime.astimezone(local_timezone)
#     return str(local_datetime_str)
