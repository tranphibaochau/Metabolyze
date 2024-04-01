import pandas as pd
import numpy as np
import sys
import os
import itertools


def get_group_names(group_ids, original_name=False):
    try:
        groups = pd.read_table(group_ids, sep="\t")
    except Exception as e:
        raise "Cannot read input file: " + str(e)

    group_dict = {}
    unique_groups = [x for x in groups.Group.unique() if x !="Blank"]
    if not original_name:
        for n in unique_groups:
            original_column_names = groups.loc[groups.Group == n].File.values.tolist()
            group_dict[n] = original_column_names
    else:
        for n in unique_groups:
            ids = groups.loc[groups.Group == n].id.values.tolist()
            group_dict[n] = ids
    return group_dict


def get_unique_comparisons(group_dict, reverse=True):
    unique_groups = list(group_dict.keys())
    unique_comparisons = []
    for L in range(0, len(unique_groups) + 1):
        for subset in itertools.combinations(unique_groups, L):
            if len(subset) == 2:
                unique_comparisons.append(subset)
    # compare both group1 vs. group2 and group2 vs group1`
    reversed_groups = []
    for comparison in unique_comparisons:
        reversed_comparison = tuple(reversed(comparison))
        reversed_groups.append(reversed_comparison)

    if (type(reverse) is bool and reverse is True):
        unique_comparisons = unique_comparisons + reversed_groups

    return unique_comparisons


def calculate_log_fold_change(input_file, group_ids, reverse=True, log2fold=True):

    # check if the groups are in group_ids file
    groups = get_group_names(group_ids)
    unique_comparisons = get_unique_comparisons(groups, reverse)
    df = pd.read_csv(input_file, sep='\t')
    for (group1, group2) in unique_comparisons:
        # find the list of all columns within each group
        group1_columns = groups[group1]
        group2_columns = groups[group2]
        col_log_fold = "".join(group1.split(" ")) + "_vs_" + "".join(
            group2.split(" ")) + "_LogFoldChange"  # column name to store Log Fold Change
        col_log2_fold = "".join(group1.split(" ")) + "_vs_" + "".join(
            group2.split(" ")) + "_Log2FoldChange"  # column name to store Log 2 Fold Change
        df[col_log_fold] = df[group1_columns].mean(axis=1)/df[group2_columns].mean(axis=1)
        df.fillna({col_log_fold: "NA"}, inplace=True)  # replace NaN values with NA for readability
        if log2fold:
            df[col_log2_fold] = np.log2(df[col_log_fold])
            df.fillna({col_log2_fold: "NA"}, inplace=True)  # replace NaN values with NA for readability


    df.to_csv(f"{os.getcwd()}/output/fold_change/fold_change.quantified", sep="\t", index=False)
    return


input_file = sys.argv[1]
group_ids = sys.argv[2]
reverse = sys.argv[3]
log2fold = sys.argv[4]
calculate_log_fold_change(input_file, group_ids, reverse, log2fold)
