import pandas as pd
import os
import sys
import plotly
import plotly.graph_objs as go


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


def draw_impact_plot(input_file, group_colors):
    df = read_table_as_dataframe(input_file)
    group_ids = read_table_as_dataframe(group_colors)
    col_impact_score = [c for c in df.columns if c.endswith("impact_score")]

    with open(f"{os.getcwd()}/output/iframe/output.html", "w+") as f:
        for col in col_impact_score:
            fig = go.Figure()
            x_random = (df[col])
            y_random = df['RT']
            # Create a trace
            trace = go.Scatter(
                x=y_random,
                y=x_random,
                mode='markers',
                text=df['Metabolite']
            )
            if len(col_impact_score) == 1:
                groups = group_ids['Group'].unique().tolist()
                title = groups[0] + " vs " + groups[1]
            else:
                groups = col.split("_")
                title = "_".join(groups[0:2]) + " vs " + "_".join(groups[2:4])
            layout = go.Layout(
                title=title,
                hovermode='closest',
                xaxis=dict(
                    title='Retention Time',
                    ticklen=5,
                    zeroline=False,
                    gridwidth=2,
                ),
                yaxis=dict(
                    title='Impact Score',
                    ticklen=5,
                    gridwidth=2,
                ),
                showlegend=False)

            fig.add_trace(trace)
            fig.update_layout(layout)
            plotly.offline.plot(fig, filename=f"{os.getcwd()}/output/impact_plot/{title}_impact_plot.html", auto_open=False)
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))


input_file = sys.argv[1]
group_colors = sys.argv[2]
draw_impact_plot(input_file, group_colors)