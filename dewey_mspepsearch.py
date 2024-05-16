import tarfile
import sys
import subprocess
import os
# output: .features

#
# Actual code begins here...
#
library_path = sys.argv[1]  # tar file including the spectral libraries
seq_name = sys.argv[2]
seq_name = seq_name.split(".")[0] # remove extension from the string

files = os.listdir(library_path)

directories = []
libraries = []
# Iterate through each file
for file in files:
    # Check if the file is a tar file
    if file.endswith('.tar'):
        # Create a full path to the tar file
        tar_file = os.path.join(library_path, file)


        # Open the tar file
        with tarfile.open(tar_file, 'r') as tar:
            extract_folder = tar.getmembers()[0].name
            if not os.path.exists(os.path.join(library_path, extract_folder)):
                # Extract all contents
                tar.extractall(path=library_path)
            for folder in tar.getmembers():
                # Check if the member is a directory
                if folder.isdir():
                    # add the folders into the libraries
                    libraries.append(folder.name.split("/")[-1])
                    directories.append(os.path.join(library_path, folder.name))


paths = {}
for i in range(len(libraries)):
    paths[libraries[i]] = directories[i]
# use wine to run MSPepSearch_x64 from ubuntu
if 'MSPepSearch_x64' not in paths:
    raise Exception('MSPepSearch_x64 not found in directories. Please import MSPepSearch_x64')
subprocess.run(["wine", f"{paths['MSPepSearch_x64']}\\MSPepSearch.exe", "d", "a", "v", "l", "G", "/Z", "0.01", "/M", "0.05", "/INP", seq_name + ".mgf"] + ["/LIB", f"{paths['nist_msms']}"] + ["/OUTTAB", f"{os.getcwd()}/output/mspepsearch/{seq_name}.txt"], stdout=subprocess.DEVNULL)
print("", file=sys.stderr, flush=True)
print("----------------", file=sys.stderr, flush=True)
print("", file=sys.stderr, flush=True)


