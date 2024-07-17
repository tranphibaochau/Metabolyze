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

hi_res_search_type = sys.argv[3]
hi_res_search_options = sys.argv[4]
lo_res_search_type = sys.argv[5]
presearch_type = sys.argv[6]
additional_options = sys.argv[7]
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


subprocess_command.extend(["/INP", seq_name]) # add input
if 'nist_msms' not in paths:
    raise Exception('nist_msms not found in directories. Please import nist_msms')
for dir in directories[1:-1]:
    subprocess_command.extend(["/LIB", dir]) # specify input and output files
subprocess_command.extend(["/OUTTAB", f"{os.getcwd()}/output.txt"])
print(subprocess_command)
print(directories)
subprocess.run(subprocess_command, stdout=subprocess.DEVNULL)
#subprocess.run(["wine", f"{paths['MSPepSearch_x64']}/MSPepSearch.exe", "d", "a", "v", "l", "G", "/Z", "0.01", "/M", "0.05", "/INP", seq_name] + ["/LIB", f"{paths['nist_msms']}"] + ["/OUTTAB", f"{os.getcwd()}/output/mspepsearch/potato.txt"], stdout=subprocess.DEVNULL)
print("", file=sys.stderr, flush=True)
print("----------------", file=sys.stderr, flush=True)
print("", file=sys.stderr, flush=True)


