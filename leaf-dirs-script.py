import sys
import os
import zipfile
import tarfile
import gzip
import shutil
from pathlib import Path

def extract_archive(input_file, temp_dir):
    """Extract compressed file based on extension"""
    if input_file.endswith('.zip'):
        with zipfile.ZipFile(input_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    elif input_file.endswith('.tar'):
        with tarfile.open(input_file, 'r') as tar_ref:
            tar_ref.extractall(temp_dir)
    elif input_file.endswith('.gz'):
        output_path = temp_dir / Path(input_file).stem
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        raise ValueError(f"Unsupported file format: {input_file}")

def get_leaf_directories(input_file):
    """
    Extract compressed file and return list of leaf directories
    
    Args:
        input_file (str): Path to compressed file (.zip, .tar, .gz)
    
    Returns:
        list: List of leaf directory paths
    """
    temp_dir = Path(f"{os.getcwd()}/temp")
    temp_dir.mkdir(exist_ok=True)
    
    extract_archive(input_file, temp_dir)
    
    leaf_dirs = []
    for root, dirs, files in os.walk(temp_dir):
        if not dirs:
            leaf_dirs.append(os.path.relpath(root, temp_dir))
            
    # Cleanup
    shutil.rmtree(temp_dir)
    
    output_dir = Path(f"{os.getcwd()}/output/leaf_dirs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "leaf_directories.txt", 'w') as f:
        for dir_path in leaf_dirs:
            f.write(f"{dir_path}\n")
    
    return leaf_dirs

if __name__ == "__main__":
    input_file = sys.argv[1]
    get_leaf_directories(input_file)