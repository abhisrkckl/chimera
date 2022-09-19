import glob
import os
import getopt
import sys


cmdargs = sys.argv[1:]
opts, args = getopt.gnu_getopt(cmdargs, "", [])

input_dir = os.path.realpath(args[0])
output_dir = os.path.realpath(args[1])
psrname = args[2]

input_ar_files = glob.glob(f"{input_dir}/CHIME_{psrname}_beam_?_?????_?????.ar")
for ar_file in input_ar_files:
    cmd = f"psrsh chime_convert_and_tfzap.psh -e zap -O {output_dir} {ar_file}"
    print(cmd)
    os.system(cmd)
