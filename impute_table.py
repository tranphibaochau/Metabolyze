import pandas as pd
import numpy as np
import os
import sys


# function to perform imputation per column
def impute(data_frame, current_col, threshold_col, impute_method):
    if impute_method == "impute_with_blank_threshold":
        return data_frame[current_col].where(data_frame[current_col] < data_frame[threshold_col],
                                             data_frame[threshold_col])
    else:
        return data_frame[current_col].where(data_frame[current_col] < data_frame[threshold_col], 0)


# impute all chosen columns with the desired value
def impute_table(blank_threshold, column_file, impute_method="impute_with_blank_threshold"):
    if impute_method == "impute_with_blank_threshold":
        print("Imputing with blank threshold")
    else:
        print("Imputing with zero")

    with open(column_file, 'r') as col_file:
        column_names = [x.strip(' "\'\t\r\n') for x in col_file.readline().split(",")]

    blank_threshold_df = pd.read_table(blank_threshold)

    for col in column_names:
        blank_threshold_df[col] = impute(blank_threshold_df, col, 'blank_threshold', impute_method)

    blank_threshold_df.drop(['blank_threshold'], axis=1, inplace=True)  # drop the comparison column
    blank_threshold_df = blank_threshold_df.loc[:,
                         ~blank_threshold_df.columns.str.contains('^Unnamed')]  # drop unnamed columns
    blank_threshold_df.to_csv(f"{os.getcwd()}/output/imputed_tables/df_table_imputed.quantified", sep="\t", index=False)
    return


blank_threshold = sys.argv[1]
column_file = sys.argv[2]
impute_method = sys.argv[3]

impute_table(blank_threshold, column_file, impute_method)
# impute_table("C:\\Users\\cpt289\Downloads\\test_files\\68dcc7b768c228d7bbbc76bdab2959a8.quantified","C:\\Users\\cpt289\\Downloads\\test_files\\sample_columns.txt")
