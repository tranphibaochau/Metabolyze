import pandas as pd
import os
import sys
import plotly
import plotly.graph_objs as go
import numpy as np
from itertools import combinations
import plotly.express as px


def read_table_as_dataframe(input_file):
    df = pd.DataFrame()
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


def draw_volcano_plot(input_file, significance_threshold=0.05, fold_change_threshold_lower=-0.5,
                      fold_change_threshold_upper=0.5, opacity=1.0):
    df = read_table_as_dataframe(input_file)
    col_ttest_pval = [c for c in df.columns if c.endswith("ttest_pval")]  # determine the p-value columns
    col_log2_foldchange = [c for c in df.columns if
                           c.endswith("Log2FoldChange")]  # determine the Log2FoldChange columns
    if len(col_ttest_pval) == 0 or len(col_log2_foldchange) == 0:
        raise KeyError("Missing ttest_pval or Log2FoldChange column(s) in input_file. Please check again!")

    title = "Volcano Plot"
    with open(f"{os.getcwd()}/output/iframe/{title}.html", "w+") as f:
        for i, c in enumerate(col_ttest_pval):
            new_df = df[df[c].notna()]
            new_df.reset_index(inplace=True)
            if len(col_ttest_pval) > 1:
                title = "Volcano Plot: " + c.split("_ttest_pval")[0]
                new_df.rename(
                    columns={c: "ttest_pval", "".join([c.split("_ttest")[0], "_Log2FoldChange"]): "Log2FoldChange"},
                    inplace=True)

            new_df['-log10(p_value)'] = -1 * np.log10(new_df['ttest_pval'])
            new_df['color'] = ((new_df['-log10(p_value)'] > -np.log10(significance_threshold)) &
                               ((new_df['Log2FoldChange'] < fold_change_threshold_lower) |
                                (new_df['Log2FoldChange'] > fold_change_threshold_upper)))
            # Create the Volcano plot using Plotly Express
            volcano_plot = px.scatter(new_df, x='Log2FoldChange', y='-log10(p_value)',
                                      color=new_df['color'],
                                      color_discrete_map={True: 'red', False: 'black'},
                                      hover_name='Metabolite',
                                      hover_data='Formula',
                                      labels={'Gene': 'Formula'},
                                      title=title,
                                      opacity=opacity)

            # Add horizontal line for significance threshold
            volcano_plot.add_shape(type='line',
                                   x0=new_df['Log2FoldChange'].min(),
                                   y0=-np.log10(significance_threshold),
                                   x1=new_df['Log2FoldChange'].max(),
                                   y1=-np.log10(significance_threshold),
                                   line=dict(color='gray', dash='dash'))

            # Add vertical lines for fold change threshold (optional)
            volcano_plot.add_shape(type='line',
                                   x0=fold_change_threshold_lower,
                                   y0=new_df['-log10(p_value)'].min(),
                                   x1=fold_change_threshold_lower,
                                   y1=new_df['-log10(p_value)'].max(),
                                   line=dict(color='gray', dash='dash'))
            volcano_plot.add_shape(type='line',
                                   x0=fold_change_threshold_upper,
                                   y0=new_df['-log10(p_value)'].min(),
                                   x1=fold_change_threshold_upper,
                                   y1=new_df['-log10(p_value)'].max(),
                                   line=dict(color='gray', dash='dash'))
            volcano_plot.update_layout(showlegend=False)
            plotly.offline.plot(volcano_plot, filename=f"{os.getcwd()}/output/volcano_plot/{title}.html",
                                auto_open=False)
            # Write all the plots as a single html file
            f.write(volcano_plot.to_html(full_html=False, include_plotlyjs='cdn'))


input_file = sys.argv[1]
significance_threshold = float(sys.argv[2])
fold_change_threshold_lower =float(sys.argv[3])
fold_change_threshold_upper = float(sys.argv[4])
opacity = float(sys.argv[5])

draw_volcano_plot(input_file, significance_threshold, fold_change_threshold_lower, fold_change_threshold_upper, opacity)
