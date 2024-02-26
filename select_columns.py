import os
import pandas as pd
import numpy as np

def select_columns(input_file, columns):
    df = pd.read_csv(input_file)
    df = df[columns]