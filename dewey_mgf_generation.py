import sys
import sqlite3
import os

study = sys.argv[1]
con = sqlite3.connect(study)
cur = con.cursor()


sample_num = cur.execute(
    "SELECT COUNT (DISTINCT name) from rawfile where ID > 0"
).fetchone()[0]
observed = cur.execute(
    "SELECT COUNT (DISTINCT rawfile) from scans where rawfile > 0"
).fetchone()[0]

if sample_num != observed:
    print("Sanity check failure: expected samples != observed files!!!", file=sys.stderr, flush=True)
    sys.exit(-1)

try:
    mass_translation_factor = cur.execute(
        "SELECT value from sequence where attribute = 'mass_translation_factor'"
    ).fetchone()[0]
    time_translation_factor = cur.execute(
        "SELECT value from sequence where attribute = 'time_translation_factor'"
    ).fetchone()[0]
except:
    mass_translation_factor = 10000  # 1 = 0.0001 Da
    time_translation_factor = 1000   # 1 = 0.001 seconds


FILE_SQL = """SELECT rawfile.id, rawfile.name FROM rawfile WHERE rawfile.id > 0 ORDER BY rawfile.id ASC"""
SCAN_SQL = """SELECT scans.scan_ID, scans.rt, scans.precursor, scans.scan_type FROM scans WHERE scans.rawfile = ? ORDER BY scans.scan_ID ASC"""
PEAK_SQL = """SELECT ms2_peaks.rawfile, ms2_peaks.rt, ms2_peaks.mz, ms2_peaks.intensity FROM ms2_peaks WHERE ms2_peaks.rawfile > 0 ORDER BY ms2_peaks.rawfile ASC, ms2_peaks.rt ASC, ms2_peaks.mz ASC"""

all_filenames = {}
for x in cur.execute(FILE_SQL):
    all_filenames[x[0]] = x[1]

seq_name = study[:-8]

scan_loader_counter = 0
scan_loader_scan_counter = 0
all_scans = {}
for (rawid, fname) in all_filenames.items():
    scan_loader_counter += 1
    print(f"processing {fname} ({scan_loader_counter}) / ({len(all_filenames.items())})", file=sys.stderr, flush=True)
    scans = {}
    prev_ms1 = None
    for x in cur.execute(SCAN_SQL, (rawid,)):
        if x[3] == "MS1":
            prev_ms1 = x[1]
        else:
            scan_loader_scan_counter += 1
            scans[x[1]] = [x[0], x[2], prev_ms1]
    all_scans[rawid] = scans

#
# MGF Generation and Search
#


with open(f"{os.getcwd()}/output.mgf", 'w+') as mgf:
    prev_rt = -1
    prev_rawid = None
    scan_count = 0
    peak_count = 0
    peaks = []  # Technically this gets taken care of in the loop, but still, defensive programming etc...
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
            pepmass = all_scans[rawid][rt][1]  # this is still a raw mz integer from the sqlite file...
            print("BEGIN IONS", file=mgf)
            if pepmass > 0:
                print(f"TITLE={all_filenames[rawid]}.{all_scans[rawid][rt][0]}.+", file=mgf)
                print("CHARGE=127+", file=mgf)
            else:
                print(f"TITLE={all_filenames[rawid]}.{all_scans[rawid][rt][0]}.-", file=mgf)
                print("CHARGE=128-", file=mgf)
            print(f"RTINSECONDS={float(rt / time_translation_factor)}", file=mgf)
            if pepmass > 0:
                print(f"PEPMASS={float(pepmass / mass_translation_factor)}", file=mgf)
            else:
                print(f"PEPMASS={-1 * float(pepmass / mass_translation_factor)}", file=mgf)
        peak_count += 1
        if mz < 0:
            peaks = [(float( (-mz) / mass_translation_factor) , intensity)] + peaks
        else:
            peaks.append((float(mz / mass_translation_factor), intensity))
    # Finalize Last Scan...
    if scan_count > 0:
        for (m, i) in peaks:
            print(f"{m} {i}", file=mgf)
        print("END IONS\n", file=mgf)