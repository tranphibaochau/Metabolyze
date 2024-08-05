import sys
import os
import base64
import zipfile
from math import pi
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import BasicTicker, PrintfTickFormatter, HoverTool, CustomJS
from bokeh.transform import linear_cmap
from bokeh.resources import CDN
from bokeh.embed import file_html
from sklearn.metrics.pairwise import pairwise_distances
from scipy.cluster.hierarchy import linkage, dendrogram
# from scipy.spatial.distance import squareform
import numpy as np


__version__ = "0.1"

node_directory = os.getcwd()

image_zip_filename = sys.argv[1]
correlations_filename = sys.argv[2]

d = pd.read_csv(correlations_filename, sep="\t")
d.set_index('mz_a', inplace=True)
d.columns.name = 'mz_b'

zip_fnames = []
zip_urls = []
with zipfile.ZipFile(image_zip_filename, "r") as f:
        for fname in f.namelist():
                zip_fnames.append(fname[:-4])
                zip_binary = f.read(fname)
                zip_base64_utf8_str = base64.b64encode(zip_binary).decode('utf-8')
                zip_dataurl = f'data:image/png;base64,{zip_base64_utf8_str}'
                zip_urls.append(zip_dataurl)
print(zip_fnames, d.columns)
for (x, y) in zip(zip_fnames, list(d.columns)):
        assert(x == y)

#Z = linkage(squareform(1-d))
Z = linkage(1-d)

results = dendrogram(Z, no_plot=True)
icoord, dcoord = results['icoord'], results['dcoord']
re_order = results['leaves']

new_urls = []
for x in re_order:
        new_urls.append(zip_urls[x])
zip_urls = new_urls

d = d.iloc[re_order]
d = d[d.columns[re_order]]

mz_a = list(d.index)
mz_b = list(d.columns) # list(reversed(d.columns))

mzs = []
print(mz_a)

for mz in mz_a:
        print("dafuq:", mz)

        the_mz = mz.split('mz')[0]
        mzs.append(f"mz={the_mz}")

d = pd.DataFrame(d.stack(), columns=['correlation']).reset_index()

d["imgs_a"] = d["mz_a"]
d["imgs_b"] = d["mz_b"]

d['mz_a_val'] = d.apply(lambda x: x['mz_a'].split("_")[1].split("(")[0], axis=1)
d['mz_b_val'] = d.apply(lambda x: x['mz_b'].split("_")[1].split("(")[0], axis=1)


# this is the colormap from the original NYTimes plot
colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]

TOOLS = "save,pan,box_zoom,reset,wheel_zoom"

p = figure(#title=f"mz correlation (slice 1)",
           x_range=mz_a, y_range=mz_b,
           x_axis_location="above", width=800, height=800,
           tools=TOOLS, toolbar_location='below')#,
           #tooltips=[('mz_pair', '@mz_a @mz_b'), ('correlation', '@correlation')])

r = p.rect(x="mz_a", y="mz_b", width=1, height=1, source=d,
           fill_color=linear_cmap("correlation", colors, low=-1.0, high=1.0),
           line_color=None)

callback = CustomJS(args= {'urls': zip_urls, 'masses': mzs}, code="""
        if(cb_data.index.indices.length > 0){
                document.getElementById('screendiv').style.visibility='visible';
                const col = Math.floor(cb_data.index.indices[0]/masses.length);
                const row = cb_data.index.indices[0] % masses.length;
                console.log(cb_data.index.indices[0], col, row, masses[col], masses[row], urls[col], urls[row]);
                document.getElementById("screen1").src = urls[col];
                document.getElementById("screen2").src = urls[row];
                document.getElementById("header1").innerHTML = masses[col];
                document.getElementById("header2").innerHTML = masses[row];
        } else {
                document.getElementById('screendiv').style.visibility='hidden';
        }
""")

hover = HoverTool(
        tooltips=None,
        callback=callback #, renderers=[r]
    )

p.add_tools(hover)

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "7px"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = pi / 3

p.add_layout(r.construct_color_bar(
    major_label_text_font_size="7px",
    ticker=BasicTicker(desired_num_ticks=len(colors)),
    formatter=PrintfTickFormatter(format="%.2f"),
    label_standoff=6,
    border_line_color=None,
    padding=5
), 'right')

p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
p.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

html = file_html(p, CDN, title="Clustered Images")

f = open(f"{node_directory}/output/iframe/viz.html", 'w')

for line in html.split("\n"):
        if line.startswith("  <body>"):
                print("""
  <body>
  <center>
  <div id="screendiv" width="800px" style="visibility: hidden">
  <table >
        <tr>
        <th id="header1">
          mass1
        </th>
        <th id="header2">
          mass2
        </th>
        </tr>
        <tr>
        <td >
                        <img id="screen1"
                    src="" height="200" width="200" style="float: left; margin: 5px 5px 5px 5px;"
                    border="2"
                ></img
        </td>
        <td>
                        <img id="screen2"
                    src="" height="200" width="200" style="float: left; margin: 5px 5px 5px 5px;"
                    border="2"
                ></img>
        </td>
        </tr>
        </table></div>
""", file=f)
        else:
                print(line, file=f)
f.close()
