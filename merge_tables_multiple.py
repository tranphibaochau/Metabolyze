import pandas as pd
import os
import sys
import itertools
import glob

def merge_tables(folder_path):
    files = os.listdir(folder_path)
    pattern = '*.features'

    # Find all TSV files in the folder
    tsv_files = glob.glob(os.path.join(folder_path, pattern))
    result = pd.DataFrame()
    # Loop through each TSV file
    for f in tsv_files:
        # Open the TSV file in read mode with appropriate encoding
        df = pd.read_table(f)
        # Create a CSV reader object with tab as the delimiter
        if result.shape[0] == 0 or result.shape[1] == df.shape[1]:
            result = pd.concat([result, df], ignore_index=True, axis=0)
    result.to_csv(os.path.join(folder_path, 'features_merged.features'), sep='\t', index=False)


folder_path = 'Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\2 - Features Merge'
merge_tables(folder_path)