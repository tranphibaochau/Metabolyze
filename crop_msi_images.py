from PIL import Image
import os
from collections import defaultdict
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


def crop_images(image_path, x_coords, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    files = os.listdir(image_path)

    for image_file in files:
        img_name = image_file.split("(")[0]  # get part of the input file name
        img_name = img_name.split(".png")[0]
        # first, crop out the blank region and metadata of the images
        with Image.open(os.path.join(image_path,image_file)) as img:
            width, height = img.size
            img = img.crop((550, 80, width-60, height-150))
            width, height = img.size
            x1, x2, x3 = x_coords  # get the x-coordinates to divide the slide image into 4 parts

            # ensure coordinates are in correct order and within image bounds
            if not (0 <= x1 < x2 < x3 <= width):
                raise ValueError("X-coordinates must be in increasing order and within image width bounds.")

            # define the bounding boxes for the four segments
            boxes = [
                (0, 0, x1, height),
                (x1, 0, x2, height),
                (x2, 0, x3, height),
                (x3, 0, width, height)
            ]
            output_paths = []
            for i in range(1, 5):
                if i<3:
                    output_paths.append(os.path.join(output_folder, f"{img_name}_s{i}_R.png"))
                else:
                    output_paths.append(os.path.join(output_folder, f"{img_name}_s{i}_NR.png"))

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
                new_image = Image.new('RGB', (500, 500), (0, 0, 0))

                # Calculate the position to paste the original image onto the new image
                paste_position = ((500 - cropped_img.width) // 2, (500 - cropped_img.height) // 2)

                # Paste the original image onto the new image
                new_image.paste(cropped_img, paste_position)
                new_image.save(output_path)
                print(f"Cropped image saved to {output_path}")
    print("Finished!")

# Example usage
crop_images('SQ1633_1915x846', [160, 440, 800], 'SQ1633_1915x846_cropped')

