import tarfile
import sys
import subprocess
import os
from pathlib import Path

#
# Actual code begins here...
#
library_path = sys.argv[1]  # tar file including the spectral libraries
seq_name = sys.argv[2]

hi_res_search_type = sys.argv[3]
hi_res_search_options = sys.argv[4]
lo_res_search_type = sys.argv[5]
presearch_type = sys.argv[6]
additional_options = sys.argv[7]
path = Path(library_path)

directories = []
libraries = []
# Iterate through each file
if os.path.isdir(path):
    for folder in path.rglob('*'):
        if folder.is_dir():
            libraries.append(folder.name.split("/")[-1])
            directories.append(os.path.join(library_path, folder.name))
elif path.suffix == ".tar":
    # Open the tar file
    with tarfile.open(path, 'r') as tar:
        extract_folder = tar.getmembers()[0].name
        current_folder = Path("\\".join(library_path.split("\\")[:-1]))
        print("current_folder", current_folder)
        tar.extractall(path=current_folder)
        for folder in tar.getmembers():
            # Check if the member is a directory
            if folder.isdir():
                # add the folders into the libraries
                libraries.append(folder.name.split("/")[-1])
                directories.append(os.path.join(current_folder, folder.name))
paths = {}
for i in range(len(libraries)):
    paths[libraries[i]] = directories[i]
# use wine to run MSPepSearch_x64 from ubuntu
if 'MSPepSearch_x64' not in paths:
    raise Exception('MSPepSearch_x64 not found in directories. Please import MSPepSearch_x64')

# based on user input, create subprocess command to run wine
subprocess_command = [f"{paths['MSPepSearch_x64']}\\MSPepSearch.exe"]
if hi_res_search_type != 'None':
    subprocess_command.append(hi_res_search_type)
if hi_res_search_options != 'None':
    subprocess_command.append(hi_res_search_options)
if lo_res_search_type != 'None':
    subprocess_command.append(lo_res_search_type)
if presearch_type != 'None':
    subprocess_command.append(presearch_type)
if additional_options != "None":
    subprocess_command.extend(additional_options.split(" "))

print(paths)
subprocess_command.extend(["/INP", seq_name])  # add input
if 'nist_msms' not in paths:
    raise Exception('nist_msms not found in directories. Please import nist_msms')
for dir in directories[1:-1]:
    subprocess_command.extend(["/LIB", dir])  # specify input and output files
subprocess_command.extend(["/OUTTAB", f"{os.getcwd()}/output.txt"])
subprocess.run([f"{paths['MSPepSearch_x64']}/MSPepSearch64.exe", "d", "a", "v", "l", "G", "/Z", "0.01", "/M", "0.05", "/INP", seq_name] + ["/LIB", f"{paths['MSP_Libraries']}"] + ["/OUTTAB", f"{os.getcwd()}/output/mspepsearch/potato.txt"], stdout=subprocess.DEVNULL)

print("", file=sys.stderr, flush=True)
print("----------------", file=sys.stderr, flush=True)
print("", file=sys.stderr, flush=True)


