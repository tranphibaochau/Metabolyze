import os
import pandas as pd
import sys


def select_columns(input_file, columns):
    try:
        df = pd.read_table(input_file, sep="\t")
        columns = pd.read_table(columns, sep="\t")
    except:
        raise Exception("Cannot read input file as pandas Dataframe")
    cols = columns['Name'].to_list()
    if all(x in df.columns for x in cols):
        df = df[cols]
    else:
        raise Exception("Columns not found in input file! Please check column name")
    df.index = df.reset_index(drop=True).index + 1
    df.to_csv(f"{os.getcwd()}/output/select_columns/df_selected.quantified", sep="\t", index=True)


input_file = sys.argv[1]
columns = sys.argv[2]
select_columns(input_file, columns)
# select_columns("C:\\Users\\cpt289\\Downloads\\test_files\\skeleton_5f3d664819ddc908977bf85d258826f4.quantified", "C:\\Users\\cpt289\Downloads\\test_files\\column_picks.tsv")