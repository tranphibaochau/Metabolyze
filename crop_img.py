from PIL import Image
import os
import sys

input_folder = sys.argv[1]
left = int(sys.argv[2])
top = int(sys.argv[3])
right = int(sys.argv[4])
bottom = int(sys.argv[5])


def crop_img(left, top, right, bottom):
    """
    Crops an image based on the given coordinates and saves the cropped image.
    :param left: The x-coordinate of the left edge of the cropping box.
    :param top: The y-coordinate of the top edge of the cropping box.
    :param right: The x-coordinate of the right edge of the cropping box.
    :param bottom: The y-coordinate of the bottom edge of the cropping box.
    """
    box = (left, top, right, bottom)
    for image_file in os.listdir(input_folder):
        image_name = image_file.split('.png')[0]
        input_path = os.path.join(input_folder, image_file)
        try:
            with Image.open(input_path) as img:
                img = img.crop(box)
                output_path = os.path.join(f"{os.getcwd()}/output/crop_img/", image_name+"_cropped.png")
                img.save(output_path)
                print(f"Cropped image saved to {output_path}")
        except (IOError, SyntaxError) as e:
            print(f"Skipped file (not an image or corrupted): {image_file}")


crop_img(left, top, right, bottom)

