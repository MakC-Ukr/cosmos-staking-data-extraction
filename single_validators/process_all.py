import pandas as pd
import datetime
import os

DEFAULT_BLOCK_TIME = 6.12345

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

def process_all(file_name):
    # file_name = "Twinstake.csv"
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'+file_name
    df = pd.read_csv(dir_path)
    new_df_ls = []
    prev_timestamp = time_to_unix(df.iloc[0]["timestamp"])
    last_block_num = df.iloc[0]["block_num"]
    for ind, row in df.iterrows():
        if ind == 0:
            row['block_len'] = DEFAULT_BLOCK_TIME
        elif row['block_num'] != last_block_num+1:
            time_diff = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
            row['block_len'] = time_diff/float(row['block_num'] - last_block_num)
        else:
            row['block_len'] = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
        new_df_ls.append(row)
        prev_timestamp = time_to_unix(row['timestamp'])
        last_block_num = row['block_num']

    new_df = pd.DataFrame(new_df_ls)
    new_df = new_df.sort_values('block_num')
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'+file_name.split('.')[0]+'_processed.csv'
    new_df.to_csv(dir_path, index=False)

process_all("Twinstake.csv")