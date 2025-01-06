import sys
import os
import zipfile
import tarfile
import gzip
import shutil
from pathlib import Path
import subprocess
#
# Actual code begins here...
#
library_path = Path(sys.argv[1])  # path to libraries for MSPepsearch
msp_path = Path(sys.argv[2])  # path to MSPepsearch
input_file = sys.argv[3]  # input file

msp_parameters = sys.argv[4] # parameters to run MS Pepsearch

directories = []


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
    temp_dir = Path(f"{os.getcwd()}/libraries")
    temp_dir.mkdir(exist_ok=True)

    extract_archive(input_file, temp_dir)

    leaf_dirs = []
    for root, dirs, files in os.walk(temp_dir):
        if not dirs:
            leaf_dirs.append(os.path.abspath(root, temp_dir))
    return leaf_dirs

def run_mspepsearch(library_path, mspepsearch_path, input_file,
                    msp_parameters="d a v l G /Z 0.01 /M 0.05 /MatchPolarity"):
    library_dirs = get_leaf_directories(library_path)
    mspepsearch_dir = get_leaf_directories(mspepsearch_path)
    print("Library directories: ", library_dirs)
    print("mspepsearch directory", mspepsearch_dir[0])
    if len(mspepsearch_dir) != 1:
        raise ValueError(f"MSPepSearch path contains more than one directory: {len()}")



    subprocess_command = [f"{mspepsearch_dir}/MSPepSearch64.exe"]
    subprocess_command.extend(["/INP", input_file])


    if msp_parameters != "None":
        subprocess_command.extend(msp_parameters.split(" "))


    for dir in library_dirs:
        subprocess_command.extend(["/LIB", str(dir)])  # add MS library directories
    subprocess_command.extend(["/OUTTAB", f"{os.getcwd()}/output/mspepsearch/output.txt"])
    subprocess.run(subprocess_command, stdout=subprocess.DEVNULL)


run_mspepsearch(library_path, msp_path, input_file, msp_parameters)


