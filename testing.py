import datetime
def time_to_unix(time):
    year = int(time.split('-')[0])
    month = int(time.split('-')[1])
    date = int(time.split('-')[2].split('T')[0])
    hour = int(time.split("T")[1].split(":")[0])
    mins = int(time.split("T")[1].split(":")[1])
    secs = int(time.split("T")[1].split(":")[2].split('.')[0])
    millisecs = int(int(time.split("T")[1].split(":")[2].split('.')[1][:-1])/1000000)
    date_time = datetime.datetime(year, month, date, hour, mins, secs)
    unix_timestamp = datetime.datetime.timestamp(date_time)*1000
    unix_timestamp+=millisecs
    return unix_timestamp

print(time_to_unix('2022-11-03T07:28:58.023539119Z'))