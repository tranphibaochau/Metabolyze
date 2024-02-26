import pandas as pd
import numpy as np
import os
# import pyarrow
import sys


def blank_threshold(input_file, column_file, signal_to_noise=3, min_signal=10000):
    if not input_file.endswith(".quantified"):
        raise ValueError("File must have .quantified extension")
    column_names = ['Metabolite']
    # get all column names to calculate the blank threshold
    with open(column_file, 'r') as col_file:
        blank_columns =[x.strip(' "\'\t\r\n') for x in col_file.readline().split(",")]

    data = pd.read_table(input_file)
    # calculate the blank threshold for each row based on signal_to_noise and min_signal
    data['blank_threshold'] = data[blank_columns].mean(axis=1) * signal_to_noise + min_signal
    data.to_csv(f"{os.getcwd()}/output/blank_threshold/df_w_threshold.quantified", sep="\t", index=True)
    return


input_file = sys.argv[1]
column_file = sys.argv[2]
min_signal = int(sys.argv[3])
signal_to_noise = int(sys.argv[4])

blank_threshold(input_file, column_file, signal_to_noise, min_signal)
#blank_threshold("C:\Data\Coffee\sqlite\skeleton_5f3d664819ddc908977bf85d258826f4.quantified", "C:\Data\Coffee\sqlite\column_names.txt", 3, 10000)


