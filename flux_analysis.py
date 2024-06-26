import pandas as pd
import sys
import os
import re

def flux_analysis(input_file):
    df = pd.read_table(input_file)
    pattern = r'^S\d+'  # check if column name follows the patter S#####
    columns = [x for x in df.columns if re.match(pattern, x)]

    original_row = None
    for i, row in df.iterrows():
        if row[0].endswith("-0"):
            if original_row is not None:
                for col in columns:
                    df.loc[original_row, col] = 100
            original_row = i

        else:
            for col in columns:
                if df.loc[original_row, col] == 0:
                    df.loc[i, col] = 100
                else:
                    try:
                        df.loc[i, col] = round(df.loc[i, col]*100/df.loc[original_row, col],2)
                    except:
                        raise ValueError(df.loc[i, col], df.loc[original_row, col])
    for col in columns:
        df.loc[original_row, col] = 100
    df.to_csv(f"{os.getcwd()}/output/flux_analysis/flux_analysis.quantified", sep="\t", index=False)


input_file = sys.argv[1]

flux_analysis(input_file)

