import pandas as pd
import numpy as np
import sys
import os
import itertools




def calculate_log_fold_change(input_file):

    try:
        df = pd.read_csv(input_file, sep='\t')
    except Exception as e:
        raise("Could not read input file: {}".format(input_file))
    if any("LogFoldChange" in x for x in df.columns):
        pass
    else:
        raise ValueError("LogFoldChange not found in input file: {}".format(input_file))
    if any("Log2FoldChange" in x for x in df.columns):
        pass
    else:
        raise ValueError("Log2FoldChange not found in input file: {}".format(input_file))
    if any("_combined_mean" in x for x in df.columns):
        pass
    else:
        raise ValueError("mean not found in input file: {}".format(input_file))
    if any("_ttest_pval" in x for x in df.columns):
        pass
    else:
        raise ValueError("mean not found in input file: {}".format(input_file))

    cols = [x for x in df.columns if x.endswith("Log2FoldChange")]
    for c in cols:
        group_comparison = "".join(c.split("_LogFoldChange")[0])
        col_impact_score = group_comparison + "_impact_score"

        df[col_impact_score] = 2**abs((df[cols]*df[group_comparison+"_combined_mean"])/(df[group_comparison+"_ttest_pval"]))
        df.fillna({col_impact_score: "NA"}, inplace=True)  # replace NaN values with NA for readability

    df.to_csv(f"{os.getcwd()}/output/impact_score/impact_score.quantified", sep="\t", index=False)
    return


input_file = sys.argv[1]
group_ids = sys.argv[2]
reverse = sys.argv[3]
log2fold = sys.argv[4]
calculate_log_fold_change(input_file, group_ids, reverse, log2fold)
