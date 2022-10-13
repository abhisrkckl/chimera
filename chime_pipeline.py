import glob
import os
import getopt
import sys
from astropy import log
from pplib import *
import pptoas as ppt
import ppalign

log.setLevel("INFO")

cmdargs = sys.argv[1:]
opts, args = getopt.gnu_getopt(cmdargs, "", [])


#Run this script as follows: python chime_pipeline.py "path to .ar files" "path were data products are to be stored" "psr jname" "post scrunch zapping file"
input_dir = os.path.realpath(args[0])
output_dir = os.path.realpath(args[1])
psrname = args[2]
dm = args[3]
dm = float(dm)
model_portrait = args[4]
#meta_file = args[5]
#pzap_file = args[4]

datafile_glob_prefix = f"{output_dir}/CHIME_{psrname}_beam_?_?????_?????"

#Run psrsh in a loop to avoid memory issues
input_ar_files = glob.glob(f"{datafile_glob_prefix}.ar")
for ar_file in input_ar_files:
    zap_cmd = f"psrsh chime_convert_and_tfzap.psh -e zap -O {output_dir} {ar_file}"
    log.info(zap_cmd)
    #os.system(zap_cmd)


#Command to scrunch to 64 frequency channels
scr_cmd = f"pam -e ftscr -u {output_dir} --setnchn 64 --setnsub 1 -d {dm} {datafile_glob_prefix}.zap"
log.info(scr_cmd)
#os.system(scr_cmd)

#Post scrunching zapping. Will need to be unique per source
pzap_cmd = f'paz -z "17 36 15 7 2 0 1 5 47 40 34" -e pzap -O {output_dir} {datafile_glob_prefix}.ftscr'
log.info(pzap_cmd)
#os.system(pzap_cmd)


#Make a metafile of the fully zapped and scrunched files
metafile_cmd = f'ls {datafile_glob_prefix}.pzap > {output_dir}/{psrname}.meta'
os.system(metafile_cmd)
meta_file = f"{output_dir}/{psrname}.meta"
#print(meta_file)
gt = ppt.GetTOAs(meta_file, model_portrait)
gt.get_TOAs(DM0=dm)

