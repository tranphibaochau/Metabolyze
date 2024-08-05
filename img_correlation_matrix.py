from PIL import Image
import os
import sys
import zipfile
from pathlib import Path
import pandas as pd
import numpy as np

input_file = sys.argv[1]


df = pd.DataFrame()
image_vectors = []
current_dir = os.getcwd()
# extract all the file inside the zip file
with zipfile.ZipFile(input_file, 'r') as z_file:
    input_folder = Path(f"{current_dir}/zip_folder")
    os.makedirs(input_folder, exist_ok=True)
    z_file.extractall(input_folder)
# list all image file inside the new extracted folder
for image_file in input_folder.rglob('*.png'):
    image_name = image_file.name.split('.png')[0]
    # open the image file and execute cropping
    img = Image.open(image_file)
    img = img.resize((64,64))
    # normalize and convert the image file to a 1D numpy array
    img_numpy = np.array(img).flatten()
    df[image_name] = img_numpy
df = df.corr()
df.to_csv(f'{current_dir}/output/correlation_matrix/output.tsv', sep="\t", index=False)
#df.to_csv(f'{current_dir}/output/correlation_matrix/output.tsv', sep="\t", index=False)