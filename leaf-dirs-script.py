import sys
import os
import zipfile
from pathlib import Path

def get_leaf_directories(input_file):
    """
    Extract zip file and return list of leaf directories (dirs with no subdirs)
    
    Args:
        input_file (str): Path to input zip file
    
    Returns:
        list: List of leaf directory paths
    """
    # Create temp directory for extraction
    temp_dir = Path(f"{os.getcwd()}/temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Extract zip contents
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    leaf_dirs = []
    
    # Walk through directory tree
    for root, dirs, files in os.walk(temp_dir):
        if not dirs:  # If no subdirectories, this is a leaf
            leaf_dirs.append(os.path.relpath(root, temp_dir))
            
    # Clean up temp directory
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    temp_dir.rmdir()
    
    # Write results to output file
    output_dir = Path(f"{os.getcwd()}/output/leaf_dirs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "leaf_directories.txt", 'w') as f:
        for dir_path in leaf_dirs:
            f.write(f"{dir_path}\n")
    
    return leaf_dirs

if __name__ == "__main__":
    input_file = sys.argv[1]
    get_leaf_directories(input_file)