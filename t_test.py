import os
import pandas as pd
import numpy as np
import itertools
import scipy
from scipy.stats import ttest_ind
import sys


def get_group_names(group_ids, original_name=False):
    try:
        groups = pd.read_table(group_ids, sep="\t")
    except Exception as e:
        raise "Cannot read input file: " + str(e)

    group_dict = {}
    unique_groups = [x for x in groups.Group.unique() if x !="Blank"]
    if original_name:
        for n in unique_groups:
            original_column_names = groups.loc[groups.Group == n].File.values.tolist()
            group_dict[n] = original_column_names
    else:
        for n in unique_groups:
            ids = groups.loc[groups.Group == n].id.values.tolist()
            group_dict[n] = ids
    return group_dict


def t_test(input_file, group_ids):
    print("\n")
    print("============================================")
    print(f"Calculating t-test between {group1} and {group2}:")

    # check if the groups are in group_ids file
    groups = get_group_names(group_ids)
    unique_groups = [x for x in groups.Group.unique() if x != 'Blank']
    if group1 not in unique_groups or group2 not in unique_groups:
        raise ValueError("Group not found! Please look at the group_ids file to find the correct groups.")

    df = pd.read_csv(input_file, sep='\t')
    # find the list of all columns within each group
    group1_columns = groups.loc[groups.Group == group1]['File'].tolist()
    group2_columns = groups.loc[groups.Group == group2]['File'].tolist()
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
    df.to_csv(f"{os.getcwd()}/output/statistical_ttest/t_test.quantified", sep="\t", index=False)


input_file = sys.argv[1]
group_ids = sys.argv[2]
group1 = sys.argv[3]
group2 = sys.argv[4]

t_test(input_file, group_ids, group1, group2)
# t_test("C:\\Users\\cpt289\\Downloads\\test_files\\df_table_imputed2.quantified",
# "C:\\Users\\cpt289\\Downloads\\test_files\\Groups.tsv", "Light Roast", "Dark Roast")
