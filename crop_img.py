from PIL import Image
import os
import sys
import shutil
import zipfile
from pathlib import Path

input_file = sys.argv[1]
left = int(sys.argv[2])
top = int(sys.argv[3])
right = int(sys.argv[4])
bottom = int(sys.argv[5])


# utility function to zip a folder
def zip_folder(input_path, output_path):
    shutil.make_archive(output_path, 'zip', input_path)


def crop_img(left, top, right, bottom):
    """
    Crops an image based on the given coordinates and saves the cropped image.
    :param left: The x-coordinate of the left edge of the cropping box.
    :param top: The y-coordinate of the top edge of the cropping box.
    :param right: The x-coordinate of the right edge of the cropping box.
    :param bottom: The y-coordinate of the bottom edge of the cropping box.
    """
    current_dir = os.getcwd()
    box = (left, top, right, bottom)
    # extract all the file inside the zip file
    with zipfile.ZipFile(input_file, 'r') as z_file:
        input_folder = Path(f"{current_dir}/zip_folder")
        os.makedirs(input_folder, exist_ok=True)
        z_file.extractall(input_folder)
    # list all image file inside the new extracted folder
    for image_file in input_folder.rglob('*.png'):
        image_name = image_file.name.split('.png')[0]
        # open the image file and execute cropping
        try:
            with Image.open(image_file) as img:
                img = img.crop(box)
                output_path = os.path.join(f"{current_dir}/output/crop_img/", image_name + "_cropped.png")
                img.save(output_path)
                print(f"Cropped image saved to {output_path}")
        except (IOError, SyntaxError) as e:
            print(f"Skipped file (not an image or corrupted): {image_file}")
    output_path = f"{current_dir}/output/crop_img/"
    # zip the folder in case using for down stream node that needs the image names intact
    zip_path = f"{current_dir}/output/crop_img_zip/output"
    zip_folder(output_path, zip_path)
    shutil.rmtree(input_folder)  # remove the unzipped folder afterwards




crop_img(left, top, right, bottom)

