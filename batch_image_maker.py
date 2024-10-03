import os
import sys
import io
import base64

import zipfile
import numpy as np
import matplotlib.pyplot as plt


__version__ = "0.1" 

node_directory = os.getcwd()

n = int(sys.argv[1])

quant_file = sys.argv[2]

min_x = 10000000000
max_x = -1
min_y = 10000000000
max_y = -1



mzs = []
mobs = []
png_data = []
with open(quant_file, 'r') as qfile:
    headers = qfile.readline()  # headers
    headers = headers.strip().split("\t")[2:]
    for header in headers:
        mob_offset = header.find("mob")
        (mz_from, mz_to) = header[2:mob_offset].split("_")
        mz_from = float(mz_from)
        mz_to = float(mz_to)
        mzs.append((mz_from + mz_to)/2)
        (mob_from, mob_to) = header[(mob_offset + 3):].split("_")
        mob_from = float(mob_from)
        mob_to = float(mob_to)
        mobs.append((mob_from + mob_to)/2)

if not n:
    n = len(mzs)

with zipfile.ZipFile(f"{node_directory}/output/zipped/images.zip", 'w') as zipped:
    for i in range(n):
        measurements = []
        with open(quant_file, 'r') as qfile:
            qfile.readline()
            for line in qfile:
                vals = line.strip().split("\t")
                x = int(vals[0])
                if x < min_x:
                    min_x = x
                if max_x < x:
                    max_x = x
                y = int(vals[1])
                if y < min_y:
                    min_y = y
                if max_y < y:
                    max_y = y
                measurements.append((x, y, float(vals[i + 2])))

        canvas = np.zeros((max_y - min_y + 1, max_x - min_x + 1))
        for (x, y, val) in measurements:
            canvas[y-min_y, x-min_x] = val

        plt.imshow(canvas, cmap='hot')
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                    hspace = 0, wspace = 0)
        plt.margins(0,0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        byte_store = io.BytesIO()
        plt.savefig(byte_store, format='png', bbox_inches = 'tight', pad_inches = 0)
        byte_store.seek(0)
        zipped.writestr(f"{mzs[i]:.3f}_{mobs[i]:.2f}.png", byte_store.read())

        png_data.append(base64.b64encode(byte_store.read()).decode())
