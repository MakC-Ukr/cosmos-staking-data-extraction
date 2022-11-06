import pandas as pd
import datetime
import os
DEFAULT_BLOCK_TIME = 6.1143
file_name = "Figment.csv"
ValidatorName = file_name.split('.')[0]

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
    ROWS_APPENDED= 0
    # file_name = "Twinstake.csv"
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'+file_name
    df = pd.read_csv(dir_path)
    df.sort_values('block_num', inplace=True)
    print(df.iloc[65:70])
    new_df_ls = []
    prev_timestamp = time_to_unix(df.iloc[0]["timestamp"])
    last_block_num = df.iloc[0]["block_num"]
    print(ROWS_APPENDED)
    for ind, row in df.iterrows():
        if ind == 0:
            row['block_len'] = DEFAULT_BLOCK_TIME
        elif row['block_num'] != last_block_num+1:
            time_diff = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
            row['block_len'] = time_diff/float(row['block_num'] - last_block_num)
        else:
            row['block_len'] = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
        row['appended_block']=0
        new_df_ls.append(row)
        prev_timestamp = time_to_unix(row['timestamp'])
        last_block_num = row['block_num']
    
        new_row = pd.Series(row).copy(deep=True)
        if ind >= len(df)-1:
            continue
        diff_from_next_row = int(df.iloc[ind+1]['block_num'] - row['block_num']-1)
        rew_diff = df.iloc[ind+1]['commission_amt'] - row['commission_amt']
        row_block_num = row['block_num']
        row_reward = row['commission_amt']
        for i in range(diff_from_next_row):
            new_row = pd.Series(new_row).copy(deep=True)
            new_row['block_num'] = row_block_num + i + 1
            new_row['commission_amt'] = row_reward + rew_diff/(diff_from_next_row+1)*(i+1)
            new_row['appended_block'] = 1
            i+=1
            new_df_ls.append(new_row)
            print(new_row[:2])
            print(new_row['commission_amt'])
            print()
            print()
            print()
            ROWS_APPENDED+=1

            
    print("Rows appended: ", ROWS_APPENDED)


    new_df = pd.DataFrame(new_df_ls)
    dir_path = os.path.dirname(os.path.realpath(__file__))+f'/{ValidatorName}_processed.csv'
    new_df.to_csv(dir_path, index=False)


# Sort
dir_path = os.path.dirname(os.path.realpath(__file__))+'/'+file_name
df = pd.read_csv(dir_path)
df.sort_values(by=['block_num'], inplace=True)
dir_path = os.path.dirname(os.path.realpath(__file__))+f'/{ValidatorName}_sorted.csv'
df.to_csv(dir_path, index=False)

# Process
process_all(f"{ValidatorName}_sorted.csv")
