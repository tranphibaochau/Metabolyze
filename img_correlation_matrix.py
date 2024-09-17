import cv2
import numpy as np
import sys
import os
import shutil
import zipfile
from pathlib import Path
import pandas as pd
import glob

# Step 1: Load Image
input_file = sys.argv[1]


def img_correlation(input_file):

    current_dir = os.getcwd()
    df = pd.DataFrame()
    # extract all the file inside the zip file
    with zipfile.ZipFile(input_file, 'r') as z_file:
        input_folder = Path(f"{current_dir}/zip_folder")
        os.makedirs(input_folder, exist_ok=True)
        z_file.extractall(input_folder)

    files = glob.glob(os.path.join(input_folder, '**', '*.png'), recursive=True)

    # rename each file to avoid handling special characters
    for index, file_path in enumerate(files):

        path = "/".join(file_path.split("/")[:-1])
        name = file_path.split("/")[-1]
        new_file_path = path + name.split()[0] + ".png"

        # Rename the file
        os.rename(file_path, new_file_path)
    # list all image file inside the new extracted folder
    mask_image = None
    bw_image = None
    for image_file in input_folder.rglob('*.png'):
        # open the image file and perform bitwise OR operation to create a mask image
        img = cv2.imread(f"{input_folder}/test_dataset/{image_file.name}")
        if bw_image is not None:
            mask_image = bw_image
        _, bw_image = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY) # turn any non-black pixel to white
        if mask_image is not None:
            mask_image = cv2.bitwise_or(mask_image, bw_image)
    mask_image = np.array(mask_image).flatten()
    non_zero_pixels = np.where(mask_image != 0)[0]
    for image_file in input_folder.rglob('*.png'):
        # open the image file and execute pruning background pixels
        img = cv2.imread(f"{input_folder}/test_dataset/{image_file.name}")
        img = np.array(img).flatten()
        img = img[non_zero_pixels]
        df[image_file.name[:-4]+ " mz"] = img
    corr = df.corr()
    corr.to_csv(f'{current_dir}/output/correlation_matrix/output.tsv', sep="\t", index=False)

    shutil.rmtree(input_folder)  # remove the unzipped folder afterwards

img_correlation(input_file)