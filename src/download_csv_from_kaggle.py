import os
import glob
import shutil
import kagglehub
import sqlite3
import pandas as pd
from settings import *

def download_raw_data_csv():
    # Download latest version
    path = kagglehub.dataset_download("davidcariboo/player-scores")

    print("Path to dataset files:", path)
    return path

def create_table_in_sqlite(path):
    conn = sqlite3.connect(os.path.join(db_path, 'Football.db'))
    csv_files = glob.glob(f"{path}/*.csv")
    print(csv_files)

    for csv_file in csv_files:
        # os.path.basename(csv_file) output = csv file name
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        print(f'Import {csv_file} to table {table_name}')

        df = pd.read_csv(csv_file)
        df.to_sql(table_name, conn, if_exists='replace', index=False)

def delete_raw_local_file(path):
    if os.path.isfile(path):
        os.remove(path)
        print('Deleted file')
    elif os.path.isdir(path):
        shutil.rmtree(path)
        print('Deleted folder')



if __name__ == "__main__":
    path = download_raw_data_csv()
    # path = r'C:\Users\ASUS\.cache\kagglehub\datasets\davidcariboo\player-scores\versions\602'
    create_table_in_sqlite(path)
    delete_raw_local_file(path)
