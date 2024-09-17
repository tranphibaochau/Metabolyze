import pandas as pd
import os
import sys


# helper function to read file as either tsv or csv depending on the separator
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


def convert_column_name(input_file, group_ids, name_to_id="True"):
    df = read_table_as_dataframe(input_file)
    group_df = read_table_as_dataframe(group_ids)
    # create a dictionary to convert column names based on Groups.tsv
    if name_to_id == "True":
        convert_names = dict([(key, value) for i, (key, value) in enumerate(zip(group_df['File'], group_df['id']))])
    else:
        convert_names = dict([(key, value) for i, (key, value) in enumerate(zip(group_df['id'], group_df['File']))])
    df.rename(columns=convert_names, inplace=True)
    df.to_csv(f"{os.getcwd()}/output/convert_column_names/output.tsv", sep="\t", index=False)


input_file = sys.argv[1]
group_ids = sys.argv[2]
name_to_id = sys.argv[3]
convert_column_name(input_file, group_ids, name_to_id)
