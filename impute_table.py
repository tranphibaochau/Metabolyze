import pandas as pd
import numpy as np
import os
import sys


# perform imputation per column
def impute(data_frame, current_col, impute_method=None):
    if impute_method == "impute_with_blank_threshold":
        return data_frame[current_col].where(data_frame[current_col] < data_frame['blank_threshold'],
                                             data_frame['blank_threshold'])
    elif impute_method == "impute_with_zero":
        return data_frame[current_col].where(data_frame[current_col] < data_frame['blank_threshold'], 0)
    # if impute_method is not specified, mark the cell as '-'
    else:
        return data_frame[current_col].where(data_frame[current_col] < data_frame['blank_threshold'], '-')


# impute all chosen columns with the desired value
def impute_table(input_file, impute_method="impute_with_blank_threshold"):
    try:
        imputed_df = pd.read_table(input_file, index_col=0)
        marked_df = pd.read_table(input_file, index_col=0)
    except Exception as e:
        raise "Cannot read input file: " + str(e)

    if 'blank_threshold' not in imputed_df.columns:
        raise KeyError("blank_threshold column not found in input_file, please merge it into the dataframe!")

    if impute_method == "impute_with_blank_threshold":
        print("Imputing with blank threshold")
    else:
        print("Imputing with zero")

    for col in imputed_df.columns:
        if col != "blank_threshold":
            imputed_df[col] = impute(imputed_df, col, impute_method)
            marked_df[col] = impute(marked_df, col)

    marked_df.drop(['blank_threshold'], axis=1, inplace=True)  # drop the comparison column
    imputed_df.drop(['blank_threshold'], axis=1, inplace=True)

    imputed_df.to_csv(f"{os.getcwd()}/output/imputed_tables/imputed_table.quantified", sep="\t", index=True)
    marked_df.to_csv(f"{os.getcwd()}/output/marked_tables/marked_table.quantified", sep="\t", index=True)
    return


input_file = sys.argv[1]
impute_method = sys.argv[2]

impute_table(input_file, impute_method)
#impute_table("C:\\Users\\cpt289\Downloads\\test_files\\test_data.quantified", "impute_with_blank_threshold")
