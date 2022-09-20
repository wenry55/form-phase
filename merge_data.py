
import os
import pandas as pd

file_list = os.listdir('./data')
for f in file_list:
    df = pd.read_csv(f'./data/{f}')
    print(df.columns)

