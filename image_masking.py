from PIL import Image
import numpy as np
import sys
import os
import shutil
import zipfile
from pathlib import Path
import pandas as pd

# Step 1: Load Image
input_file = sys.argv[1]

# utility function to zip a folder
def zip_folder(input_path, output_path):
    shutil.make_archive(output_path, 'zip', input_path)


def mask_img(input_file):

    current_dir = os.getcwd()
    df = {}
    # extract all the file inside the zip file
    with zipfile.ZipFile(input_file, 'r') as z_file:
        input_folder = Path(f"{current_dir}/zip_folder")
        os.makedirs(input_folder, exist_ok=True)
        z_file.extractall(input_folder)
    # list all image file inside the new extracted folder
    mask_image = None
    for image_file in input_folder.rglob('*.png'):
        # open the image file and execute cropping
        with Image.open(image_file).convert('L') as img:
            if mask_image is None:
                mask_image = Image.new('L', img.size, 0)
                mask_image = np.array(mask_image).flatten()
            img = np.array(img).flatten()
            mask_image = np.bitwise_or(mask_image, img)
    non_zero_pixels = np.where(mask_image > 0)[0]  # find indexes of non-black pixels
    for image_file in input_folder.rglob('*.png'):
        # open the image file and execute cropping
        with Image.open(image_file).convert('L') as img:
            img = np.array(img).flatten()
            img = img[non_zero_pixels]
            df[image_file.name] = img
    df = pd.DataFrame.from_dict(df)
    corr = df.corr()
    corr.to_csv(f'{current_dir}/output/correlation_matrix/output.tsv', sep="\t", index=False)


    shutil.rmtree(input_folder)  # remove the unzipped folder afterwards

mask_img(input_file)