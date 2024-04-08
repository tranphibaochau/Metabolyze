import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from itertools import chain
import itertools
import sys
import os


COLORS = ['#FF0000', '#0000FF', '#000000', '#008000', '#FFFF00', '#800080', '#FFC0CB', "#c0feff", "#5b2d8c",
                  "#7f8c2d", "#F1948A", "#BB8FCE", "#AED6F1", "#A3E4D7", "#F7DC6F", "#DC7633", "#5D6D7E", "#7B7D7D"]
def draw_heatmap(input_file, group_ids, p_value=0.05, z_score=0, standard_scale=None, row_cluster=True, col_cluster=True, width=100, height=100):
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
        if input_file.endswith("quantified") or input_file.endswith("csv"):
            df = pd.read_table(input_file, sep=",", index_col=0)
        else:
            df = pd.read_table(input_file, sep="\t", index_col=0)
    except Exception as e:
        raise "Cannot read input file: " + str(input_file)
    df.set_index('Metabolite', inplace=True)  # set the name of the metabolyte to be the index
    group_dict = get_group_names(group_ids)
    name_id_list = list(group_dict.values())  # get a list lists containing (col_name, id) tuple for each column in a single group
    name_id_list = list(chain.from_iterable(name_id_list))  # flatten the nested list
    col_renames = {}
    for col in name_id_list:
        col_renames[col[0]] = col[1]
    df.rename(columns=col_renames, inplace=True)

    # calculate the number of comparisons between groups before plotting
    unique_groups = list(group_dict.keys())
    unique_comparisons = []
    for L in range(0, len(unique_groups) + 1):
        for subset in itertools.combinations(unique_groups, L):
            if len(subset) == 2:
                unique_comparisons.append(subset)

    for comp in unique_comparisons:

        pvalue_col = comp[0].strip() + "_vs_" + comp[1].strip() + "_ttest_pval"

        if pvalue_col not in df.columns:
            raise KeyError("Cannot find the pvalue column")

        plot_columns = [x[1] for x in (group_dict[comp[0]] + group_dict[comp[1]])]  # keep only the columns belong to one of the groups
        sub_df = df[df[pvalue_col] < p_value]  # filter rows that fall under the p_value threshold
        sub_df = sub_df[plot_columns]

        colors = ['#043177', '#244B88', '#FAFAFA', '#C62E2E', '#BF0F0F']
        # Create a custom colormap using LinearSegmentedColormap
        color_map = LinearSegmentedColormap.from_list('custom', colors, N=50)
        plot_dimension = str(sub_df.shape[1]) + "x" + str(sub_df.shape[0])
        plot_title = ("/output/heatmaps/plot.heatmap." + str(p_value) + comp[0].strip() + "_vs_" + comp[1].strip()
                      + "." + plot_dimension + ".pdf")

        sns_plot = sns.clustermap(data=sub_df, z_score=z_score, standard_scale=standard_scale,
                                  row_cluster=row_cluster, col_cluster=col_cluster, cmap=color_map, yticklabels=False)

        plot_destination = f"{os.getcwd()}{plot_title}"
        # Save the plot as a PDF file
        sns_plot.figure.savefig(plot_destination)


input_file = sys.argv[1]
group_ids = sys.argv[2]
z_score = sys.argv[3]
standard_scale = sys.argv[4]
if z_score == "row":
    z_score = 0
elif z_score == "column":
    z_score = 1
else:
    z_score = None
if z_score is not None:
    standard_scale = None
else:
    if standard_scale == "row":
        standard_scale = 0
    elif standard_scale == "col":
        standard_scale = 1
    else: standard_scale = None
row_cluster = sys.argv[5]
col_cluster = sys.argv[6]
row_cluster = False if row_cluster == "False" else True
col_cluster = False if col_cluster == "False" else True

draw_heatmap(input_file, group_ids)
#draw_heatmap("skeleton.quantified", "test_groups.tsv")

