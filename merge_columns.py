import pandas as pd
import os
import sys


def merge_columns(df1, df2, left_most="Table 1"):
    df1 = pd.read_table(df1, sep='\t', index_col=0)
    df2 = pd.read_table(df2, sep='\t', index_col=0)
    if df1.shape[0] != df2.shape[0]:
        raise ValueError("The two dataframes must have the same number of rows.")
    if left_most == "Table 1":
        result = pd.merge(df1, df2, left_index=True, right_index=True)
    else:
        result = pd.merge(df2, df1, left_index=True, right_index=True)
    result.to_csv(f"{os.getcwd()}/output/merge_columns/df.quantified", sep="\t", index=True)


df1 = sys.argv[1]
df2 = sys.argv[2]
left_most = sys.argv[3]
merge_columns(df1, df2, left_most)