import os
import pandas as pd
import itertools
import sys


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


def get_unique_comparisons(group_dict, reverse="False"):
    unique_groups = list(group_dict.keys())
    unique_comparisons = []
    for L in range(0, len(unique_groups) + 1):
        for subset in itertools.combinations(unique_groups, L):
            if len(subset) == 2:
                unique_comparisons.append(subset)
    # compare both group1 vs. group2 and group2 vs group1`
    reversed_groups = []
    for comparison in unique_comparisons:
        reversed_groups.append(comparison[::-1])

    if reverse == "True":
        unique_comparisons = unique_comparisons + reversed_groups
    return unique_comparisons


def calculate_combined_mean(input_file, group_ids, reverse="False"):
    # check if the groups are in group_ids file
    groups = get_group_names(group_ids)
    unique_comparisons = get_unique_comparisons(groups, reverse)
    df = pd.read_csv(input_file, sep='\t')
    for (group1, group2) in unique_comparisons:
        group1_mean_col = group1.replace(" ", "") + "_mean"
        group2_mean_col = group2.replace(" ", "") + "_mean"
        if group1_mean_col not in df.columns or group2_mean_col not in df.columns:
            raise Exception(group1_mean_col + " or " + group2_mean_col + " not found in input file")
        combined_mean_col = group1.replace(" ", "") + "_vs_" + group2.replace(" ", "") + "_combined_mean"
        df[combined_mean_col] = df[group1_mean_col] + df[group2_mean_col]
    df.to_csv(f"{os.getcwd()}/output/combined_mean/combined_mean.quantified", sep="\t", index=False)

input_file = sys.argv[1]
group_ids = sys.argv[2]
reverse = sys.argv[3]

calculate_combined_mean(input_file, group_ids, reverse)