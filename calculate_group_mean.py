import pandas as pd
import numpy as np
import os
import sys


def calculate_group_means(input_file, group_ids):
    def get_group_names(group_ids, original_name=False):
        try:
            groups = pd.read_table(group_ids, sep="\t")
        except Exception as e:
            raise "Cannot read input file: " + str(e)

        group_dict = {}
        unique_groups = [x for x in groups.Group.unique() if x != "Blank"]
        if not original_name:
            for n in unique_groups:
                original_column_names = groups.loc[groups.Group == n].File.values.tolist()
                group_dict[n] = original_column_names
        else:
            for n in unique_groups:
                ids = groups.loc[groups.Group == n].id.values.tolist()
                group_dict[n] = ids
        return group_dict

    try:
        df = pd.read_csv(input_file, sep="\t")
    except Exception as e:
        raise "Cannot read input file: " + str(e)
    group_dict = get_group_names(group_ids)
    for group in group_dict:
        col_name = group + "_mean"
        group_ids = group_dict[group]
        df[col_name] = df[group_ids].mean(axis=1)
    df.to_csv(f"{os.getcwd()}/output/group_means/group_means.quantified", sep="\t", index=False)
    return


input_file = sys.argv[1]
group_ids = sys.argv[2]
calculate_group_means("skeleton_coffee.quantified", "Groups.tsv")
