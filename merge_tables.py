import pandas as pd
import numpy as np
import os
import sys
import glob

def merge_tables(folder_path, output_file):
    files = os.listdir(folder_path)
    pattern = '*.quantified'
    # Find all TSV files in the folder
    tsv_files = glob.glob(os.path.join(folder_path, pattern))
    result = pd.read_table(tsv_files[0], sep='\t')

    # Loop through each TSV file
    for f in tsv_files[1:]:
        # Open the TSV file in read mode with appropriate encoding
        df = pd.read_table(f)
        result_columns = result.columns
        df_columns = df.columns
        added_columns = df_columns.difference(result_columns)
        df = df[added_columns]
        result = pd.merge(result, df, left_index=True, right_index=True)
        result.reset_index(drop=True, inplace=True)
    result.to_csv(output_file, sep="\t", index=False)


merge_tables("Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization", "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\7 - Columns Merge\\1551_1555_columns_merged.quantified")
