import pandas as pd
import os
import sys

def read_table_as_dataframe(input_file):
    try:
        df = pd.read_table(input_file, sep="\t")
        if len(df.columns) == 1 and len(df.columns[0].split(",")) > 1:
            df = pd.read_table(input_file, sep=",")
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.EmptyDataError:
        print("Empty file.")
    except Exception as e:
        print("Error occurred:", e)
    return df

def calculate_blank_threshold(input_file, signal_to_noise=3, min_signal=10000):
    df = read_table_as_dataframe(input_file)
    blank_columns = [x for x in df.columns.unique() if "Blank" in x]
    df['blank_threshold'] = df[blank_columns].mean(axis=1) * signal_to_noise + min_signal  # calculate blank threshold
    df['blank_threshold'] = df['blank_threshold'].round().astype(int)  # round to the nearest integer
    df[blank_columns] = 0  # correcting the blank columns to be 0 after calculating the blank threshold
    df.index = df.reset_index(drop=True).index + 1  # insert index column for merging purposes

    df.to_csv(f"{os.getcwd()}/output/calculate_blank_threshold/df_w_threshold.quantified", sep="\t", index=False)


input_file = sys.argv[1]
signal_to_noise = int(sys.argv[2])
min_signal = int(sys.argv[3])

calculate_blank_threshold(input_file, signal_to_noise, min_signal)
# calculate_blank_threshold("C:\\Users\\cpt289\\Downloads\\test_files\\blank_columns_selected.quantified", 3, 10000)


