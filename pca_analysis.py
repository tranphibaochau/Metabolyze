import pandas as pd
import numpy as np
import itertools
import os
from functools import reduce
from get_group_ids import get_group_names


def sequence2id(result):
    ids = get_group_names('ID').items()

    for x, y in ids.items():
        result.rename(columns={x: y}, inplace=True)
        # Returns matrix based on inputted IDS
    return result


def pca_analysis(input_file, group_dict, reverse=False):
    """
    perform pca analysis between all comparison groups
    :param input_file:
    :param group_dict:
    :param reverse: whether or not we perform reverse comparison (group1 vs group2 and group2 vs group1)
    """
    unique_groups = list(group_dict.keys())

    unique_comparisons=[]
    for L in range(0, len(unique_groups) + 1):
        for subset in itertools.combinations(unique_groups, L):
            if len(subset) == 2:
                unique_comparisons.append(subset)
    # compare both group1 vs. group2 and group2 vs group1`
    reversed_groups = []
    for comparison in unique_comparisons:
        reversed_comparison = tuple(reversed(comparison))
        reversed_groups.append(reversed_comparison)

    if reverse is True:
        unique_comparisons = unique_comparisons + reversed_groups
    for comparison in unique_comparisons:
        matrices = []
        # print (comparison[0])

        comparison_ids = []
        for condition in comparison:
            if condition in group_dict:
                ids = (group_dict[condition])
                matrices.append()
                comparison_ids.append(ids)



        pca_matrix = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True), matrices)
        # pca_matrix = pd.DataFrame(pca_matrix).set_index('Metabolite')
        pca_matrix.index.name = 'Metabolite'

        pca_matrix = sequence2id(pca_matrix)

        pca_matrix.to_csv(f"{os.getcwd()}/output/pca_table.quantified", sep="\t", index=True)