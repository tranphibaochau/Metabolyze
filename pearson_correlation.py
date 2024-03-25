import pandas as pd
import numpy as np
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


def get_correlation(input_file, group_ids, group):
    df = pd.read_table(input_file, sep="\t")
    ids = get_group_names(group_ids)[group]
    df = df[ids]
    temp_pearson_dict={}
    cov = df.loc[df['Group'] == group]['Covariate']

    for row in df.iterrows():
        index, data = row
        pearson_correl = np.corrcoef(data, cov)[0, 1]
        temp_pearson_dict[index] = pearson_correl

    pearson_df = pd.DataFrame([temp_pearson_dict]).T
    pearson_df.columns = [group]
    return pearson_df


print(get_correlation("skeleton_coffee.quantified", "Groups.tsv", "Light Roast"))