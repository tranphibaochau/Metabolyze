import pandas as pd
import os
import matplotlib

matplotlib.use('Agg')
import numpy as np
from scipy import *
from scipy import stats
from sklearn.decomposition import PCA
import plotly
import plotly.graph_objs as go
from matplotlib import rcParams
import sys
from itertools import combinations

rcParams['pdf.fonttype'] = 42  ## Output Type 3 (Type3) or Type 42 (TrueType)
rcParams['font.sans-serif'] = 'Arial'


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


def get_group_columns(group_ids, original_name=False):
    groups = read_table_as_dataframe(group_ids)
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


def perform_PCA(df, standardize=3, log=True):
    ## preprocessing of the fpkmMatrix
    if log:
        df = np.log10(df + 1.)
    if standardize == 2:  # standardize along rows/genes
        df = stats.zscore(df, axis=1)
    elif standardize == 1:  # standardize along cols/samples
        df = stats.zscore(df, axis=0)

    ## remove genes with NaNs
    df = df[~np.isnan(np.sum(df, axis=1))]

    pca = PCA(n_components=None)
    ## get variance captured
    pca.fit(df.T)
    variance_explained = pca.explained_variance_ratio_[0:3]
    variance_explained *= 100
    ## compute PCA and plot
    pca_transformed = pca.transform(df.T)
    return variance_explained, pca_transformed


def draw_pca_plot(input_file, group_ids):
    df = read_table_as_dataframe(input_file)
    # df.index = df['Metabolite']
    # df = df.astype(float)

    group_df = read_table_as_dataframe(group_ids)
    group_df = group_df.loc[group_df['Group'] != 'Blank']
    group_df = group_df[group_df['id'].isin(df.columns)]  # keep only rows that contain column names in df
    unique_groups = group_df['Group'].unique().tolist()
    group_dict = get_group_columns(group_ids, True)
    # if there are more than two groups in the input, make a combination of comparisons



    group_df.index = group_df['id']
    colors = group_df['Color'].unique().tolist()
    df = df.reindex(columns=group_df['id'].tolist())
    groups = group_df['Group'].unique().tolist()
    variance_explained, pca_transformed = perform_PCA(df.values, standardize=2, log=True)

    group_df['x'] = pca_transformed[:, 0]
    group_df['y'] = pca_transformed[:, 1]
    group_df['z'] = pca_transformed[:, 2]

    sub_df_list = []
    if len(unique_groups) > 2:
        for subset in combinations(unique_groups, 2):
            grp1, grp2 = subset
            grp1_cols = group_dict[grp1]
            grp2_cols = group_dict[grp2]
            comparison_df = df[grp1_cols + grp2_cols]
            sub_df_list.append(comparison_df)
    rows = len(sub_df_list)+1
    cols = 1
    with (open(f"{os.getcwd()}/output/pca_plot/output.html", "w+") as f,
          open(f"{os.getcwd()}/output/iframe/output.html", "w+") as iframe):
        fig = go.Figure()
        for grp in groups:
            sub_df = group_df[group_df['Group'] == grp]
            # Iteratate through samples grouped by condition and platform
            display_name = '%s' % grp
            # Initiate a Scatter3d instance for each group of samples specifying their coordinates
            # and displaying attributes including color, shape, size and etc.
            trace = go.Scatter3d(
                x=sub_df['x'],
                y=sub_df['y'],
                z=sub_df['z'],
                text=sub_df['Group'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=colors[groups.index(grp)],  # Color by infection status
                    opacity=.8,
                ),
                name=display_name,
            )

            fig.add_trace(trace)
            fig.update_layout(dict(height=1000, width=1200,
                          title='3D PCA plot',
                          scene=dict(
                              xaxis=dict(title='PC1 (%.2f%% variance)' % variance_explained[0]),
                              yaxis=dict(title='PC2 (%.2f%% variance)' % variance_explained[1]),
                              zaxis=dict(title='PC3 (%.2f%% variance)' % variance_explained[2])
                          )
                          ))
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        iframe.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

        if len(sub_df_list) > 0:
            for i, sub_df in enumerate(sub_df_list):
                fig = go.Figure()

                sub_group_df = group_df[group_df['id'].isin(sub_df.columns)]  # keep only rows that contain column names in df
                sub_group_colors = sub_group_df['Color'].unique().tolist()
                sub_df = sub_df.reindex(columns=sub_group_df['id'].tolist())
                variance_explained, pca_transformed = perform_PCA(sub_df.values, standardize=2, log=True)

                sub_group_df['x'] = pca_transformed[:, 0]
                sub_group_df['y'] = pca_transformed[:, 1]
                sub_group_df['z'] = pca_transformed[:, 2]
                groups = sub_group_df['Group'].unique().tolist()
                for grp in groups:
                    grp_df = sub_group_df[sub_group_df['Group'] == grp]
                    # Iteratate through samples grouped by condition and platform
                    display_name = '%s' % grp
                    # Initiate a Scatter3d instance for each group of samples specifying their coordinates
                    # and displaying attributes including color, shape, size and etc.
                    trace = go.Scatter3d(
                        x=grp_df['x'],
                        y=grp_df['y'],
                        z=grp_df['z'],
                        text=grp_df['Group'],
                        mode='markers',
                        marker=dict(
                            size=10,
                            color=sub_group_colors[groups.index(grp)],  # Color by infection status
                            opacity=.8,
                        ),
                        name=display_name,
                    )

                    fig.add_trace(trace)
                fig.update_layout(dict(height=1000, width=1200,
                                   title='3D PCA plot',
                                   scene=dict(
                                       xaxis=dict(title='PC1 (%.2f%% variance)' % variance_explained[0]),
                                       yaxis=dict(title='PC2 (%.2f%% variance)' % variance_explained[1]),
                                       zaxis=dict(title='PC3 (%.2f%% variance)' % variance_explained[2])
                                   )
                                   ))
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                iframe.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))



input_file = sys.argv[1]
groups_path = sys.argv[2]

draw_pca_plot(input_file, groups_path)
