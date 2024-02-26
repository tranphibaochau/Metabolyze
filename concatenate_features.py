import os
import pandas as pd


def concatenate_features(file1, file2):
    if not (file1.endswith('feature') and file2.endswith('feature')):
        raise IOError("Files must end with .feature.")
    df1 = pd.read_table(file1, sep='\t')
    df2 = pd.read_table(file2)
    if df1.shape[1] != df2.shape[1]:
        raise Exception('Error! Difference in number of columns between two files!')
    elif df1.columns != df2.columns:
        raise Exception('Error! Difference in column names between two files!')
    else:
        df = pd.concat([df1, df2], axis=1)
        df.to_csv(f"{os.getcwd()}/output/blank_threshold/df_concatenated.feature", sep="\t", index=False)
