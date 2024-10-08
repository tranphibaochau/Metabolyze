from PIL import Image
import os
from collections import defaultdict
import sys
import zipfile
from pathlib import Path
import shutil


input_file = sys.argv[1]
x1 = int(sys.argv[2])
x2 = int(sys.argv[3])
x3 = int(sys.argv[4])
output_width = int(sys.argv[5])
output_height = int(sys.argv[6])

def find_non_black_pixels(img):
    img = img.convert("RGB")  # ensure the image is in RGB mode
    width, height = img.size
    coords = defaultdict(tuple)

    # helper function to determine if the pixel is not black
    def is_non_black(pixel):
        return pixel != (0, 0, 0)

    # find top-most non-black pixel
    for y in range(height):
        for x in range(width):
            if is_non_black(img.getpixel((x, y))):
                coords["top_most"] = (x, y)
                break
        if coords["top_most"]:
            break

    # find bottom-most non-black pixel
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if is_non_black(img.getpixel((x, y))):
                coords["bottom_most"] = (x, y)
                break
        if coords["bottom_most"]:
            break

    # Find left-most non-black pixel
    for x in range(width):
        for y in range(height):
            if is_non_black(img.getpixel((x, y))):
                coords["left_most"] = (x, y)
                break
        if coords["left_most"]:
            break

    # find right-most non-black pixel
    for x in range(width - 1, -1, -1):
        for y in range(height):
            if is_non_black(img.getpixel((x, y))):
                coords["right_most"] = (x, y)
                break
        if coords["right_most"]:
            break

    return coords


def crop_msi_images(x1=0, x2=0, x3=0, output_width=500, output_height=500):
    if x1 != 0 and x2 != 0 and x3 != 0:
        # ensure coordinates are in correct order and within image bounds
        if not (0 <= x1 < x2 < x3):
            raise ValueError("X-coordinates must be in increasing order!")

    current_dir = os.getcwd()
    # extract all the file inside the zip file
    with zipfile.ZipFile(input_file, 'r') as z_file:
        input_folder = Path(f"{current_dir}/zip_folder")
        os.makedirs(input_folder, exist_ok=True)
        z_file.extractall(input_folder)
    # list all image file inside the new extracted folder
    original_width, original_height = output_width, output_height
    for image_file in input_folder.rglob('*.png'):
        img_name = image_file.name.split("(")[0]  # get part of the input file name
        img_name = img_name.split(".png")[0]
        # first, crop out the blank region and metadata of the images
        with Image.open(os.path.join(input_folder, image_file)) as img:
            width, height = img.size
            if x3 > width:
                raise ValueError("X-coordinates must within image width bounds!")
            # if x1, x2, x3 are specified, cut the images into parts
            if x1 != 0 and x2 != 0 and x3 != 0:
                boxes = [
                    (0, 0, x1, height),
                    (x1, 0, x2, height),
                    (x2, 0, x3, height),
                    (x3, 0, width, height)
                ]
                output_paths = []
                for i in range(1, 5):
                    output_paths.append(os.path.join(f"{os.getcwd()}/output/crop_msi_images/", f"{img_name}_s{i}.png"))
                # crop and save
                for box, output_path in zip(boxes, output_paths):
                    cropped_img = img.crop(box)
                    coords = find_non_black_pixels(cropped_img)
                    # crop the images based on its non-black pixels
                    left = coords["left_most"][0] - 20
                    top = coords["top_most"][1] - 20
                    right = coords["right_most"][0] + 20
                    bottom = coords["bottom_most"][1] + 20
                    cropped_img = cropped_img.crop((left, top, right, bottom))

                    # if cropped image is bigger than the specified size, don't add black background to the image
                    size = max(output_width, output_height, cropped_img.width, cropped_img.height)
                    new_image = Image.new('RGB', (size, size), (0, 0, 0))
                    # Calculate the position to paste the original image onto the new image
                    paste_position = (
                        (size - cropped_img.width) // 2, (size - cropped_img.height) // 2)
                    # Paste the original image onto the new image
                    new_image.paste(cropped_img, paste_position)
                    new_image = new_image.resize((output_width, output_height))
                    new_image.save(output_path)
            else:
                coords = find_non_black_pixels(img)
                # crop the images based on its non-black pixels
                left = coords["left_most"][0] - 20
                top = coords["top_most"][1] - 20
                right = coords["right_most"][0] + 20
                bottom = coords["bottom_most"][1] + 20
                cropped_img = img.crop((left, top, right, bottom))
                if output_width == 0 and output_height == 0:
                    cropped_img.save(f"{os.getcwd()}/output/crop_msi_images/{img_name}.png")
                else:
                    # remember the image size we want to save
                    # if cropped image is bigger than the specified size, don't add black background to the image
                    size = max(output_width, output_height, cropped_img.width, cropped_img.height)
                    new_image = Image.new('RGB', (size, size), (0, 0, 0))
                    # Calculate the position to paste the original image onto the new image
                    paste_position = (
                    (size - cropped_img.width) // 2, (size - cropped_img.height) // 2)
                    # Paste the original image onto the new image
                    new_image.paste(cropped_img, paste_position)
                    new_image = new_image.thumbnail((500, 500))
                    print(f"Resized size: {new_image.size}")
                    new_image.save(f"{os.getcwd()}/output/crop_msi_images/{img_name}.png")
    shutil.rmtree(input_folder)  # remove the unzipped folder afterwards
# Example usage
crop_msi_images(x1, x2, x3, output_width, output_height)

