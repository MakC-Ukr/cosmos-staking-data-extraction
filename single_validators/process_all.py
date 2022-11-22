import pandas as pd
import datetime
import os

# params to set
DEFAULT_BLOCK_TIME = 6.5
file_name = "multiple.csv"
OutputName = file_name.split('.')[0]
N_validators = 3

# convert zulu time to unix timestamp
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

# @param df - DataFrame containing Data Extraction code
def process_all(df):
    # Read the dataframe and sort by values
    ROWS_APPENDED= 0
    df.sort_values(by=['block_num'], inplace=True)
    
    new_df_ls = []
    prev_timestamp = time_to_unix(df.iloc[0]["timestamp"])
    last_block_num = df.iloc[0]["block_num"]
    print(ROWS_APPENDED)
    for ind, row in df.iterrows():
        if ind == 0:
            row['block_len'] = DEFAULT_BLOCK_TIME# for the first row the block length can be set to 6.5 s
        elif row['block_num'] != last_block_num+1:
            # in case we missed a block in between during dat extraction, replace block length with the average time
            time_diff = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
            row['block_len'] = time_diff/float(row['block_num'] - last_block_num)
        else:
            # Otherwise block lenght is time difference between two consecutive blocks
            row['block_len'] = float(time_to_unix(row['timestamp']) - prev_timestamp)/1000.0
        row['appended_block']=0

        new_df_ls.append(row)
        prev_timestamp = time_to_unix(row['timestamp'])
        last_block_num = row['block_num']
    
        new_row = pd.Series(row).copy(deep=True)

        if ind >= len(df)-1:
            continue # continue if the row is last row of the DataFrame

        diff_from_next_row = int(df.iloc[ind+1]['block_num'] - row['block_num']-1)

        rew_diffs = []
        for i in range(N_validators):
            # Find the commission differences for two consecutive rows for all validators 
            rew_diffs.append(df.iloc[ind+1][f'val_{i}_com_amt'] - row[f'val_{i}_com_amt']) 

        row_block_num = row['block_num']
        row_rewards = []
        for i in range(N_validators):
            # Find the current commissions for two consecutive rows for all validators 
            row_rewards.append(row[f'val_{i}_com_amt']) 

        for i in range(diff_from_next_row):
            new_row = pd.Series(new_row).copy(deep=True)
            new_row['block_num'] = row_block_num + i + 1

            for i in range(N_validators):
                new_row[f'val_{i}_com_amt'] = row_rewards[i] + rew_diffs[i]/(diff_from_next_row+1)*(i+1)

            new_row['appended_block'] = 1
            i+=1
            new_df_ls.append(new_row)  
            
    print("Rows appended: ", ROWS_APPENDED)
    # get the processed DataFrame
    new_df = pd.DataFrame(new_df_ls)
    dir_path = os.path.dirname(os.path.realpath(__file__))+f'/{OutputName}_processed.csv'
    new_df.to_csv(dir_path, index=False)

# Sort
dir_path = os.path.dirname(os.path.realpath(__file__))+'/'+file_name
df = pd.read_csv(dir_path)
process_all(df)