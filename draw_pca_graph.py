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
    group_df.index = group_df['id']
    colors = group_df['Color'].unique().tolist()
    df = df.reindex(columns=group_df['id'].tolist())

    variance_explained, pca_transformed = perform_PCA(df.values, standardize=2, log=True)

    group_df['x'] = pca_transformed[:, 0]
    group_df['y'] = pca_transformed[:, 1]
    group_df['z'] = pca_transformed[:, 2]

    data = []
    # print(group_df)
    conditions = group_df['Group'].unique().tolist()

    for condition in conditions:
        sub_df = group_df[group_df['Group'] == condition]
        # Iteratate through samples grouped by condition and platform
        display_name = '%s' % (condition)
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
                color=colors[conditions.index(condition)],  # Color by infection status
                opacity=.8,
            ),
            name=display_name,
        )

        data.append(trace)

    # Configs for layout and axes
    layout = dict(height=1000, width=1200,
                  title='3D PCA plot',
                  scene=dict(
                      xaxis=dict(title='PC1 (%.2f%% variance)' % variance_explained[0]),
                      yaxis=dict(title='PC2 (%.2f%% variance)' % variance_explained[1]),
                      zaxis=dict(title='PC3 (%.2f%% variance)' % variance_explained[2])
                  )
                  )
    fig = dict(data=data, layout=layout)

    plotly.offline.plot(fig, filename=f"{os.getcwd()}/output/pca_plot/pca.html")


input_file = sys.argv[1]
groups_path = sys.argv[2]

draw_pca_plot("skeleton_grp1_grp3.tsv", "test_groups.tsv")
