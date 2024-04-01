import pandas as pd
import sys
import os


# correct all blank columns to be 0
def correct_blank_columns(input_file):
    df = pd.read_csv(input_file, index_col=0)
    df[:] = 0
    df.to_csv(f"{os.getcwd()}/output/blank_columns_corrected/blank_columns_corrected.quantified", sep="\t", index=True)
    return