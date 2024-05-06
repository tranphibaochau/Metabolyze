import pandas as pd
import os
import sys
import re


def srm_normalization(input_file, output_file=None):
    df = pd.read_table(input_file, sep="\t")
    srm_columns = [x for x in df.columns if "SRM" in x]

    df['srm_average'] = df[srm_columns].mean(axis=1)
    intensity_columns = [x for x in df.columns if x.startswith("S")
                         and "Blank" not in x]
    for col in intensity_columns:
        df[col] = df[col]/df['srm_average']
    df.drop(['srm_average'], axis=1, inplace=True)
    df.to_csv(output_file, sep="\t", index=False)

input1 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\5 - Blank Threshold Correction\\1551_blank_threshold_imputed.quantified"
input2 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\5 - Blank Threshold Correction\\1552_blank_threshold_imputed.quantified"
input3 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\5 - Blank Threshold Correction\\1553_blank_threshold_imputed.quantified"
input4 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\5 - Blank Threshold Correction\\1554_blank_threshold_imputed.quantified"
input5 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\5 - Blank Threshold Correction\\1555_blank_threshold_imputed.quantified"

output1 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization\\1551_srm_normalized.quantified"
output2 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization\\1552_srm_normalized.quantified"
output3 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization\\1553_srm_normalized.quantified"
output4 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization\\1554_srm_normalized.quantified"
output5 = "Z:\\jonesd28labspace\\4 Core Sequences\\Sequence_1551\\SQ1551-1555 Batch integrate\\6 - SRM Normalization\\1555_srm_normalized.quantified"

srm_normalization(input1, output1)
srm_normalization(input2, output2)
srm_normalization(input3, output3)
srm_normalization(input4, output4)
srm_normalization(input5, output5)