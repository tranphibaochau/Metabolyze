import pandas as pd
import numpy as np
import sys
import os
import subprocess as sp
import warnings
import itertools
from rpy2.robjects import pandas2ri, r
warnings.filterwarnings("ignore")


def draw_heatmap(input_file, group_ids, group1=None, group2=None, p_value=0.05):
    def get_group_names(group_ids):
        try:
            groups = pd.read_table(group_ids, sep="\t")
        except Exception as e:
            raise "Cannot read input file: " + str(e)
        group_dict = {}
        unique_groups = [x for x in groups.Group.unique() if x != "Blank"]
        for n in unique_groups:
            file_names = groups.loc[groups.Group == n].File.values.tolist()
            ids = groups.loc[groups.Group == n].id.values.tolist()
            group_dict[n] = list(zip(file_names, ids))
        return group_dict

    try:
        df = pd.read_table(input_file, sep=",", index_col=0)
        group_dict = get_group_names(group_ids)
    except Exception as e:
        raise "Cannot read input files. Please try again!"

    if group1 is not None and group1 not in group_dict:
        raise f"{group1} not found in Groups.tsv"
    if group2 is not None and group2 not in group_dict:
        raise f"{group2} not found in Groups.tsv"

    p_value_col = group1 + "_vs_" + group2 + "_ttest_pval"
    grp1_cols = [x[1] for x in group_dict[group1]]
    grp2_cols = [x[1] for x in group_dict[group2]]

    comparison_df = df[itertools.chain([df.columns[1]], grp1_cols, grp2_cols, [p_value_col])]
    comparison_df.rename(columns={p_value_col: "ttest_pval"}, inplace=True)
    comparison_df.to_csv("whatever.tsv", sep="\t", index=False)
    #comparison_df = pandas2ri.py2rpy(comparison_df)

    proc = sp.run(['Rscript','heatmap.R', 'C:\\Scripts\\Metabolyze\\whatever.tsv', 'C:\\Scripts\\Metabolyze\\test_groups.tsv', '0.05'])
    #r(r_script)
draw_heatmap("skeleton.quantified", "test_groups.tsv", group1="Group_1", group2="Group_3")

