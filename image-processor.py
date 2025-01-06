import sys
import os
import cv2
import numpy as np
from pathlib import Path

def normalize_images(input_dir):
    """
    Convert images to grayscale and normalize intensity to 0-255 range
    
    Args:
        input_dir (str): Path to directory containing images
    """
    # create output directory
    output_dir = Path(f"{os.getcwd()}/output/normalized_images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # supported image extensions
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    
    # process each image
    input_path = Path(input_dir)
    for img_path in input_path.iterdir():
        if img_path.suffix.lower() in valid_extensions:
            # Read image
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"Warning: Could not read {img_path}")
                continue
                
            # convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # normalize to 0-255 range
            if gray.max() != gray.min():  # Avoid division by zero
                normalized = np.zeros_like(gray, dtype=np.uint8)
                cv2.normalize(gray, normalized, 0, 255, cv2.NORM_MINMAX)
            else:
                normalized = gray  # If image is uniform, keep original values
            
            # Save processed image
            output_path = output_dir / f"normalized_{img_path.name}"
            cv2.imwrite(str(output_path), normalized)
            
            # Print processing info
            print(f"Processed {img_path.name}:")
            print(f"  Original range: {gray.min()}-{gray.max()}")
            print(f"  New range: {normalized.min()}-{normalized.max()}")
    
    print(f"\nProcessed images saved to: {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python normalize_images.py <input_directory>")
        sys.exit(1)
        
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)
        
    normalize_images(input_dir)