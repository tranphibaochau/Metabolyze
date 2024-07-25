import pandas as pd
import os
import sys

input_file_1 = sys.argv[1]
input_file_2 = sys.argv[2]


def read_table_as_dataframe(input_file):
    df = pd.DataFrame()
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


def replace_values(df_a, df_b):
    for idx, col in df_a.items():
        for i, val in col.items():
            if df_b.loc[i, idx] == '-':
                df_a.loc[i, idx] = df_b.loc[i, idx]
    df_a.to_csv(f"{os.getcwd()}/replaced_values.quantified", sep="\t", index=False)


df1 = read_table_as_dataframe(input_file_1)
df2 = read_table_as_dataframe(input_file_2)

replace_values(df1, df2)
