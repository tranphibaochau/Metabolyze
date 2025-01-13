import pandas as pd
import numpy as np
from scipy import stats
import sys
import os


def read_table_as_dataframe(input_file):
    try:
        df = pd.read_table(input_file, sep="\t")
        if len(df.columns) == 1 and len(df.columns[0].split(",")) > 1:
            df = pd.read_table(input_file, sep=",")
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.EmptyDataError:
        print("Empty file.")
    except Exception as e:
        print("Error occurred:", e)
    return df

def get_confidence_interval_mask(arr, confidence):
    """
    Returns a boolean mask identifying values within the confidence interval
    Args:
        arr: numpy array of values
        confidence: confidence level (default 0.95 for 95%)
    Returns:
        mask: boolean array where True indicates values within CI
    """
    if confidence > 1.0 or confidence < 0:
        raise ValueError("Confidence must be between 0 and 1")
    mean = np.mean(arr)
    sem = stats.sem(arr)  # Standard error of mean
    ci = stats.t.interval(confidence, len(arr)-1, mean, sem)
    return ci

def hotspot_removal(input_file, confidence):
    """
    Returns a dataframe with intensity values being adjusted to be within the confidence interval
    Args:
        input_file: tabular input file (either .csv or .tsv)
        confidence: confidence level (default 0.95 for 95%)
    Returns:
        df: output dataframe
    """
    df = read_table_as_dataframe(input_file)
    mz_cols = [x for x in df.columns if "mz" in x]
    for col in mz_cols:
        np_array = df[col].values.copy()
        if np.max(np_array) > 0:
            lower_bound, upper_bound = get_confidence_interval_mask(np_array, confidence)
            lower_bound = int(lower_bound)
            upper_bound = int(upper_bound)
            np.maximum(np_array, lower_bound)  # set minimum values of the array to be lower bound
            np.minimum(np_array, upper_bound)  # set maximum values of the array to be upper bound
            df[col] = np_array
    return df


input_file = sys.argv[1]
confidence = float(sys.argv[2])
output_df = hotspot_removal(input_file, confidence)
output_df.to_csv(f"{os.getcwd()}/output/hotspot_removal/hotspot_removal_output.tsv", sep="\t", index=False)
