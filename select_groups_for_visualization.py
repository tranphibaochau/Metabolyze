import pandas as pd
import sys
import os
import warnings
import itertools


def read_table_as_dataframe(input_file):
    try:
        df = pd.read_table(input_file, sep="\t")
        if len(df.columns) == 1 and len(df.columns[0].split(",")) > 1:
            df = pd.read_table(input_file, sep=",")
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.EmptyDataError:
        print("Empty file.")
    except Exception as e:
        print("Error occurred:", e)
    return df
def select_groups(input_file, group_ids, group1="All", group2="All"):
    def get_group_names(input_file):
        groups = read_table_as_dataframe(input_file)
        group_dict = {}
        unique_groups = [x for x in groups.Group.unique() if x != "Blank"]
        for n in unique_groups:
            file_names = groups.loc[groups.Group == n].File.values.tolist()
            ids = groups.loc[groups.Group == n].id.values.tolist()
            group_dict[n] = list(zip(file_names, ids))
        return group_dict

    # read input file
    df = read_table_as_dataframe(input_file)
    group_df = read_table_as_dataframe(group_ids)
    # get dictionary of group name and corresponding columns
    group_dict = get_group_names(group_ids)
    # pick a color for each group for visualization
    group_df['Color'] = 'NA'
    colors = ['#FF0000', '#0000FF', '#000000', '#008000', '#FFFF00', '#800080', '#FFC0CB', "#c0feff", "#5b2d8c",
              "#7f8c2d", "#F1948A", "#BB8FCE", "#AED6F1", "#A3E4D7", "#F7DC6F", "#DC7633", "#5D6D7E", "#7B7D7D"]
    zipped_up = zip(colors, list(group_dict.keys()))
    for x, y in zipped_up:
        group_df.loc[group_df.Group == y, 'Color'] = x

    if group1 =="All" and group2 == "All":
        df.to_csv(f"{os.getcwd()}/output/selected_groups/output.tsv", sep="\t", index=False)
        group_df.to_csv(f"{os.getcwd()}/output/group_colors/groups.tsv", sep="\t", index=False)
        return
    elif group1 == "All" or group2 == "All":
        raise Exception(f"{group1} and {group2} must both be All, or be specified")
    if group1 not in group_dict:
        raise KeyError(f"{group1} not found in Groups.tsv")
    if group2 not in group_dict:
        raise KeyError(f"{group2} not found in Groups.tsv")

    # rename statistics columns
    p_value_col = group1.replace(" ", "_") + "_vs_" + group2.replace(" ", "_") + "_ttest_pval"
    impact_col = group1.replace(" ", "_") + "_vs_" + group2.replace(" ", "_") + "_impact_score"
    logfoldchange_col = group1.replace(" ", "_") + "_vs_" + group2.replace(" ", "_") + "_Log2FoldChange"
    statistics_col = []
    if p_value_col in df.columns:
        statistics_col.append(p_value_col)
    else:
        warnings.warn(f"{p_value_col} not found in input_file!", category=UserWarning)
    if impact_col in df.columns:
        statistics_col.append(impact_col)
    else:
        warnings.warn(f"{impact_col} not found in input_file!", category=UserWarning)
    if logfoldchange_col in df.columns:
        statistics_col.append(logfoldchange_col)
    else:
        warnings.warn(f"{impact_col} not found in input_file!", category=UserWarning)
    grp1_cols = [x[1] for x in group_dict[group1]]
    grp2_cols = [x[1] for x in group_dict[group2]]
    comparison_df = df[itertools.chain(['Metabolite', 'Formula', 'RT'], grp1_cols, grp2_cols, statistics_col)]
    comparison_df.to_csv(f"{os.getcwd()}/select_groups_output.tsv", sep="\t", index=False)
    if group1 != "All":
        group_df = group_df[group_df['Group'].isin([group1, group2])]
    group_df.to_csv(f"{os.getcwd()}/groups_output.tsv", sep="\t", index=False)


input_file = sys.argv[1]
group_ids = sys.argv[2]
group1 = sys.argv[3]
group2 = sys.argv[4]
select_groups(input_file, group_ids, group1, group2)


