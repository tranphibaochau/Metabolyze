import sys
import os
import cv2
import numpy as np
from pathlib import Path
from scipy import stats


def normalize_data(flattened_np):
    print("Before normalization")
    print("Pixel Intensity Min and Max: ", np.min(flattened_np), np.max(flattened_np))
    non_black_pixels = flattened_np[flattened_np > 0]


    # calculate the mean and standard deviation
    mean = np.mean(non_black_pixels)
    std_dev = np.std(non_black_pixels)
    print(np.min(non_black_pixels), np.max(non_black_pixels), np.mean(non_black_pixels), np.median(non_black_pixels))

    lower_bound = max(mean - 1.96 * std_dev, 0)
    upper_bound = min(mean + 1.96 * std_dev, 255)


    is_within_bounds = (flattened_np > lower_bound) & (flattened_np < upper_bound)

    # create a copy of the data for modification
    rescaled_np = flattened_np.copy()

    # set values outside the confidence interval to 0
    rescaled_np[(rescaled_np <= lower_bound) | (rescaled_np >= upper_bound)] = 0

    # rescale values within the confidence interval to the range 0-255
    if np.any(is_within_bounds):  # check if there are values within the bounds
        values_within_bounds = rescaled_np[is_within_bounds]


        min_val = np.min(values_within_bounds)
        max_val = np.max(values_within_bounds)

        rescaled_values = (((values_within_bounds - min_val)/(max_val-min_val)) * 255).astype(int)

        # assign back the rescaled values
        rescaled_np[is_within_bounds] = rescaled_values
    return rescaled_np


def normalize_images(input_dir):
    # create output directory
    output_dir = Path(f"{os.getcwd()}/output/normalized_images")
    output_dir.mkdir(parents=True, exist_ok=True)
    valid_extensions = {'.jpg', '.jpeg', '.png'}

    input_path = Path(input_dir)
    for img_path in input_path.iterdir():
        if img_path.suffix.lower() in valid_extensions:
            # read and convert to grayscale
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"Warning: Could not read {img_path}")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            flattened_img = gray.flatten()
            # Process image
            normalized = normalize_data(flattened_img)
            normalized = normalized.reshape(gray.shape)

            # save processed image
            output_path = output_dir / f"normalized_{img_path.name}"
            cv2.imwrite(str(output_path), normalized)
            print("Processed ", img_path.name)
    print(f"\nProcessed images saved to: {output_dir}")
#data = np.array([0, 0, 0, 0, 1, 2, 3, 9, 9, 9, 9, 9, 10, 12, 11, 9, 9, 9, 9, 10, 100, 15, 35, 90, 150, 190, 188, 189, 182, 185, 255])
#print("testing data", data)
#print("normalized testing data", normalize_data(data))
normalize_images(sys.argv[1])