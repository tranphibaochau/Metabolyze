import pandas as pd
import numpy as np
import os
import sys


def merge_tables(input_file1, input_file2):
    try:
        df1 = pd.read_table(input_file1, sep="\t", index_col=0)
        df2 = pd.read_table(input_file2, sep="\t")
    except Exception as e:
        raise "Cannot read input files! Please check the file format."
    if df1.shape[0] != df2.shape[0]:
        raise "Error! Number of rows in two tables do not match. Cannot merge!"

    df1_columns = df1.columns
    df2_columns = df2.columns
    added_columns = df2_columns.difference(df1_columns)
    df1.reset_index(inplace=True)
    df2 = df2[added_columns]
    df2.reset_index(inplace=True)
    df = pd.merge(df1, df2, left_index=True, right_index=True)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(f"{os.getcwd()}/output/merged_table/merged_table.quantified", sep="\t", index=False)


input_file1 = sys.argv[1]
input_file2 = sys.argv[2]
merge_tables(input_file1, input_file2)
