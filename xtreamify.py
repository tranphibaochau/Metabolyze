import sys
import os
import xml.etree.ElementTree as ET
import zlib
import time
import struct
from collections import defaultdict


__version__ = "0.0.1"

start_time = time.time()

node_directory = os.getcwd()

mass_resolution = int(sys.argv[1])  # 3 (digits after the decimal point)
mob_resolution = int(sys.argv[2])  # 2 (digits after the decimal point)

baseline_filter = int(sys.argv[3])  # 100

mass_translation_factor = 10**(mass_resolution)
mob_translation_factor = 10**(mob_resolution)

mzML = sys.argv[4]  # .imzML
zstream = open(sys.argv[5], 'rb')

out = open(f"{node_directory}/output/xtream.bin", 'wb')
out.write(struct.pack('<2I', mass_translation_factor, mob_translation_factor))
tree = ET.parse(mzML)

spectrum_count = 0
peak_count = 0
filtered_peaks = 0
eliminated_spectra = 0
root = tree.getroot()
last_one_hundred = time.time()
print("STARTED XTREAM FILE")
for spectrum in root.find("{http://psi.hupo.org/ms/mzml}run/{http://psi.hupo.org/ms/mzml}spectrumList"):
    bindata = {}
    x_val = int(spectrum.find("{http://psi.hupo.org/ms/mzml}scanList/{http://psi.hupo.org/ms/mzml}scan/{http://psi.hupo.org/ms/mzml}cvParam[@accession='IMS:1000050']").attrib['value'])
    y_val = int(spectrum.find("{http://psi.hupo.org/ms/mzml}scanList/{http://psi.hupo.org/ms/mzml}scan/{http://psi.hupo.org/ms/mzml}cvParam[@accession='IMS:1000051']").attrib['value'])
    spectrum_count += 1

    for darray in spectrum.find("{http://psi.hupo.org/ms/mzml}binaryDataArrayList"):
        dref = darray.find("{http://psi.hupo.org/ms/mzml}referenceableParamGroupRef").attrib['ref']
        dextlen = int(darray.find("{http://psi.hupo.org/ms/mzml}cvParam[@accession='IMS:1000103']").attrib['value'])
        denclen = int(darray.find("{http://psi.hupo.org/ms/mzml}cvParam[@accession='IMS:1000104']").attrib['value'])
        doffset = int(darray.find("{http://psi.hupo.org/ms/mzml}cvParam[@accession='IMS:1000102']").attrib['value'])
        bindata[dref] = (dextlen, denclen, doffset)
    zstream.seek(bindata["mzArray"][2])
    ds = "d" * bindata["mzArray"][0]
    mzs = struct.unpack(ds, zlib.decompress(zstream.read(bindata["mzArray"][1])))
    zstream.seek(bindata["intensityArray"][2])
    assert(bindata["intensityArray"][0] == bindata["mzArray"][0])
    ys = struct.unpack(ds, zlib.decompress(zstream.read(bindata["intensityArray"][1])))
    zstream.seek(bindata["mobilityArray"][2])
    assert(bindata["mobilityArray"][0] == bindata["mzArray"][0])
    mobs = struct.unpack(ds, zlib.decompress(zstream.read(bindata["mobilityArray"][1])))
    keepers = []
    for (mz, mobility, intensity) in zip(mzs, mobs, ys):
        intensity_int = int(round(intensity))
        mz_int = int(round(mz * mass_translation_factor))
        mob_int = int(round(mobility * mob_translation_factor))
        if intensity_int < baseline_filter:
            filtered_peaks += 1
            continue
        peak_count += 1
        keepers.append((mz_int,  mob_int, intensity_int))
    if len(keepers) == 0:
        eliminated_spectra += 1
        print(f"Eliminated Spectrum: {x_val, y_val}")
        continue
    else:
        agg = defaultdict(int)
        for (mz_int, mob_int, intensity_int) in keepers:
            agg[(mz_int, mob_int)] += intensity_int
        out.write(struct.pack('<3I', x_val, y_val, len(agg)))  # X Y PeakNum
        for (mz_int, mob_int) in agg.keys():
            out.write(struct.pack('<3I', mz_int, mob_int, agg[(mz_int, mob_int)]))

    if (spectrum_count % 100) == 0:
        now = time.time()
        print(f"processed spectrum #{spectrum_count - 100} to {spectrum_count} in {now - last_one_hundred:.2f} seconds...")
        last_one_hundred = now

out.close()


stop_time = time.time()

print(f"Xtreamification of {spectrum_count} spectra ({eliminated_spectra} eliminated) containing {peak_count + filtered_peaks} peaks ({filtered_peaks} rejected, {peak_count} remaining) in {stop_time - start_time :.2f} seconds.", flush=True)
