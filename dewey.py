import sys
import time
import sqlite3
import subprocess
import os

__version__ = "0.1"
# this is a new one
start_time = time.time()

node_directory = os.getcwd()

study = sys.argv[1]  # .sqlite3
Metlin = sys.argv[2] == "True"
NIST = sys.argv[3] == "True"
LipidBLAST = sys.argv[4] == "True"
decoy = sys.argv[5] == "True"
HITS = int(sys.argv[6])

# output: .features

#
# Actual code begins here...
#

import tarfile
import sys
import time
import sqlite3
import subprocess
import os


spectral = sys.argv[1]  # tar file including the spectral libraries
mspepsearch = sys.argv[2]  # tar file including mspepsearch
study = sys.argv[1]  # .sqlite3
Metlin = sys.argv[2] == "True"
NIST = sys.argv[3] == "True"
LipidBLAST = sys.argv[4] == "True"
decoy = sys.argv[5] == "True"
HITS = int(sys.argv[6])


with tarfile.open(spectral, 'r') as spectral:
    print("List of directories and files inside the tar archive:")
    root = spectral.getmembers()[0].name
    spectral_directory = os.getcwd() + root

__version__ = "0.1"
# this is a new one
start_time = time.time()


# output: .features

#
# Actual code begins here...
#

libraries = []

libraries.append(spectral_directory + "/LIB")
libraries.append(spectral_directory + "/data/nist_msms")
libraries = []

if NIST:
    libraries.append(spectral_directory + "/LIB")
    libraries.append(spectral_directory + "/data/nist_msms")
    if decoy:
        libraries.append(spectral_directory + "/LIB")
        libraries.append(spectral_directory + "/data/DECOY_nist_msms")

if Metlin:
    libraries.append(spectral_directory + "/LIB")
    libraries.append(spectral_directory + "/data/METLIN_EXPERIMENTAL")
    if decoy:
        libraries.append(spectral_directory + "/LIB")
        libraries.append(spectral_directory + "/data/DECOY_METLIN_EXPERIMENTAL")

if LipidBLAST:
    libraries.append(spectral_directory + "/LIB")
    libraries.append(spectral_directory + "/data/LipidBlast_MBX")
    if decoy:
        libraries.append(spectral_directory + "/LIB")
        libraries.append(spectral_directory + "/data/DECOY_LipidBlast_MBX")

if not libraries:
    print("No spectral library specified!!!", flush=True, file=sys.stderr)
    sys.exit(-1)


class Thing:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


# By convention, we require access to a parameter (in this case NIST) prior to taking an action which
# modifies the system, this is for the bizarre case where someone might attempt to run a command template
# directly from the command line -- this should fail due access to an undefined parameter _before_ any
# damage is done to the system.

out = open(
    f"{os.getcwd()}/output/DeweyOutput/output.features", "w")

#
# Set up our cursor
#
con = sqlite3.connect(study)
cur = con.cursor()

#
# First, a sanity check (somewhat repetitive to later code, but this is temporary and will be removed when all unsafe raw2sql
# generation will have been eliminated from the lab, along with any incorrect sqlite3 file...
#

sample_num = cur.execute(
    "SELECT COUNT (DISTINCT name) from rawfile where ID > 0").fetchone()[0]
observed = cur.execute(
    "SELECT COUNT (DISTINCT rawfile) from scans where rawfile > 0").fetchone(
    )[0]

if sample_num != observed:
    print("Sanity check failure: expected samples != observed files!!!",
          flush=True, file=sys.stderr)
    sys.exit(-1)

#
# Second, load mass_translation and time_translation factors, if they are available...
# TODO: Potentially factor this code out into a module that manages access to our db format.
#

try:
    mass_translation_factor = cur.execute(
        "SELECT value from sequence where attribute = 'mass_translation_factor'"
    ).fetchone()[0]
    time_translation_factor = cur.execute(
        "SELECT value from sequence where attribute = 'time_translation_factor'"
    ).fetchone()[0]
except:
    mass_translation_factor = 10000  # 1 = 0.0001 Da
    time_translation_factor = 1000  # 1 = 0.001 seconds

FILE_SQL = """SELECT rawfile.id, rawfile.name FROM rawfile WHERE rawfile.id > 0 ORDER BY rawfile.id ASC"""
SCAN_SQL = """SELECT scans.scan_ID, scans.rt, scans.precursor, scans.scan_type FROM scans WHERE scans.rawfile = ? ORDER BY scans.scan_ID ASC"""
PEAK_SQL = """SELECT ms2_peaks.rawfile, ms2_peaks.rt, ms2_peaks.mz, ms2_peaks.intensity FROM ms2_peaks WHERE ms2_peaks.rawfile > 0 ORDER BY ms2_peaks.rawfile ASC, ms2_peaks.rt ASC, ms2_peaks.mz ASC"""

all_filenames = {}
for x in cur.execute(FILE_SQL):
    all_filenames[x[0]] = x[1]

seq_name = study[:-8]

scan_loader_start = time.time()
scan_loader_counter = 0
scan_loader_scan_counter = 0
all_scans = {}
for (rawid, fname) in all_filenames.items():
    scan_loader_counter += 1
    print(
        f"processing {fname} ({scan_loader_counter}) / ({len(all_filenames.items())})",
        flush=True)
    scans = {}
    prev_ms1 = None
    for x in cur.execute(SCAN_SQL, (rawid, )):
        if x[3] == "MS1":
            prev_ms1 = x[1]
        else:
            scan_loader_scan_counter += 1
            scans[x[1]] = [x[0], x[2], prev_ms1]
    all_scans[rawid] = scans
scan_loader_stop = time.time()
print(
    f"{scan_loader_scan_counter} scans loaded in {scan_loader_stop - scan_loader_start:.2f} seconds",
    flush=True)

#
# MGF Generation and Search
#

mgf_make_start = time.time()

mgf = open(seq_name + ".mgf", 'w')

start_query = time.time()
prev_rt = -1
prev_rawid = None
scan_count = 0
peak_count = 0
peaks = [
]  # Technically this gets taken care of in the loop, but still, defensive programming etc...
peak_counter = 0  # TODO: duplicate counter used purely for visual feedback, should be removed.
for (rawid, rt, mz, intensity) in cur.execute(PEAK_SQL):
    # NOTE: rt and mz are still raw integers unmodified by time and mass factors!!!
    peak_counter += 1
    if not (peak_counter % 100000):
        print(f"peaks processed = {peak_counter} ", flush=True)
    if rawid != prev_rawid or rt != prev_rt:
        # Finalize Scan...
        if scan_count > 0:
            for (m, i) in peaks:
                print(f"{m} {i}", file=mgf)
            print("END IONS\n", file=mgf)
        peaks = []
        prev_rt = rt
        prev_rawid = rawid
        scan_count += 1
        pepmass = all_scans[rawid][rt][
            1]  # this is still a raw mz integer from the sqlite file...
        print("BEGIN IONS", file=mgf)
        if pepmass > 0:
            print(f"TITLE={all_filenames[rawid]}.{all_scans[rawid][rt][0]}.+",
                  file=mgf)
            print("CHARGE=127+", file=mgf)
        else:
            print(f"TITLE={all_filenames[rawid]}.{all_scans[rawid][rt][0]}.-",
                  file=mgf)
            print("CHARGE=128-", file=mgf)
        print(f"RTINSECONDS={float(rt / time_translation_factor)}", file=mgf)
        if pepmass > 0:
            print(f"PEPMASS={float(pepmass / mass_translation_factor)}",
                  file=mgf)
        else:
            print(f"PEPMASS={-1 * float(pepmass / mass_translation_factor)}",
                  file=mgf)
    peak_count += 1
    if mz < 0:
        peaks = [(float((-mz) / mass_translation_factor), intensity)] + peaks
    else:
        peaks.append((float(mz / mass_translation_factor), intensity))
# Finalize Last Scan...
if scan_count > 0:
    for (m, i) in peaks:
        print(f"{m} {i}", file=mgf)
    print("END IONS\n", file=mgf)
stop_query = time.time()
mgf.close()

mgf_make_stop = time.time()
print(f"MGF created in {mgf_make_stop - mgf_make_start:.2f} seconds.",
      flush=True)
print(
    f"sql2mgf phase processed {peak_count} peaks and {scan_count} scans from {len(all_filenames)} files in {mgf_make_stop - start_time :.2f} seconds.",
    flush=True)
print("", flush=True)
print("----------------", flush=True)
print("", flush=True)

with open("test.txt", "w+") as test:
    subprocess.run([
        "/data/mspepsearch/mspepsearch", "d", "a", "v", "l", "G", "/Z", "0.01",
        "/M", "0.05", "/INP", seq_name + ".mgf"
    ] + libraries + [
        "/OUTTAB", seq_name + ".txt", "/HITS", f"{HITS}", "/MinMF", "1",
        "/OutPrecursorType", "/OutChemForm", "/OutPrecursorMZ", "/OnlyFound"
    ], stderr=test)
print("", flush=True)
print("----------------", flush=True)
print("", flush=True)

f = open(seq_name + ".txt")

print(
    "Source\tMCRL_Score\tScore\tDot\tRevDot\tProb\tMetabolite\tFormula\tIon Type\tRT (min)",
    file=out)
for line in f:
    if line.startswith(">") or line.startswith("Unknown"):
        continue
    vals = line.strip().split("\t")
    rt = float(vals[0].split(":")[1])
    # 0.01 because python rounds 1.5 _down_... (!?!)
    print(
        f"{vals[0]}\t{round(0.01 + (int(vals[8])+int(vals[10]))/2)}\t{vals[7]}\t{vals[8]}\t{vals[10]}\t{vals[9]}\t{vals[11]}\t{vals[13]}\t{vals[14]}\t{rt}",
        file=out)
out.close()
f.close()
