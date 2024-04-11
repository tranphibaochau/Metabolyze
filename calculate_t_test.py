import os
import pandas as pd
import numpy as np
import itertools
from scipy.stats import ttest_ind
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


def get_unique_comparisons(group_dict, reverse="True"):
    unique_groups = list(group_dict.keys())
    unique_comparisons = []
    # get combinations of groups for comparison
    for subset in itertools.combinations(unique_groups, 2):
        unique_comparisons.append(subset)
    # compare both group1 vs. group2 and group2 vs group1`
    reversed_groups = []
    for comparison in unique_comparisons:
        reversed_groups.append(comparison[::-1])

    if reverse == "True":
        unique_comparisons = unique_comparisons + reversed_groups

    return unique_comparisons


def t_test(input_file, group_ids, reverse="True"):
    # check if the groups are in group_ids file
    groups = get_group_names(group_ids)
    unique_comparisons = get_unique_comparisons(groups, reverse)
    df = pd.read_csv(input_file, sep='\t')
    for (group1, group2) in unique_comparisons:
        # find the list of all columns within each group
        group1_columns = groups[group1]
        group2_columns = groups[group2]
        # create sub dataframe for each group before calculating p_values
        grp1 = df[group1_columns]
        grp2 = df[group2_columns]

        p_values = []
        for i, row in grp1.iterrows():
            first = grp1.iloc[i]
            second = grp2.iloc[i]
            p_value = ttest_ind(first, second)[1]
            p_values.append(p_value)
        col_name = "".join(group1.split(" ")) + "_vs_" + "".join(group2.split(" ")) + "_ttest_pval"  # column name to store p-value
        df[col_name] = p_values
        df.fillna({col_name: "NA"}, inplace=True)  # replace NaN values with NA for readability
    df.to_csv(f"{os.getcwd()}/output/ttest_pval/ttest_pval.quantified", sep="\t", index=False)


input_file = sys.argv[1]
group_ids = sys.argv[2]
reverse = sys.argv[3]

t_test(input_file, group_ids, reverse)
