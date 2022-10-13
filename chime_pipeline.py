import glob
import os
import getopt
import sys
from astropy import log
from pplib import *
import pptoas as ppt
import ppalign
import subprocess

log.setLevel("INFO")

class Session:
    """Class for storing command line arguments and other global state."""
    
    def __init__(self, argv):
        cmdargs = sys.argv[1:]
        opts, args = getopt.gnu_getopt(cmdargs, "", [])

        #Run this script as follows: python chime_pipeline.py "path to .ar files" "path were data products are to be stored" "psr jname" "post scrunch zapping file"
        self.input_dir = os.path.realpath(args[0])
        self.output_dir = os.path.realpath(args[1])
        self.psrname = args[2]
        self.dm = float(args[3])
        self.model_portrait = args[4]
        self.test_mode = False
        #meta_file = args[5]
        #pzap_file = args[4]
    
        self.datafile_glob_prefix = f"CHIME_{self.psrname}_beam_?_?????_?????"

def run_cmd(cmd, test_mode):
    try:
        log.info(cmd)
        if not test_mode:
            p = subprocess.Popen(cmd, shell=True)
            p.wait()
    except:
        raise OSError("Error while executing command.\ncmd :: "+cmd)

if __name__ == "__main__":

    session = Session(sys.argv)

    #Run psrsh in a loop to avoid memory issues
    input_ar_files = glob.glob(f"{session.input_dir}/{session.datafile_glob_prefix}.ar")
    for ar_file in input_ar_files:
        prefix = os.path.splitext(os.path.basename(ar_file))[0]
        
        zap_cmd = f"psrsh chime_convert_and_tfzap.psh -e zap -O {session.output_dir} {session.input_dir}/{prefix}.ar"
        run_cmd(zap_cmd, session.test_mode)

        #Command to scrunch to 64 frequency channels
        scr_cmd = f"pam -e ftscr -u {session.output_dir} --setnchn 64 --setnsub 1 -d {session.dm} {session.output_dir}/{prefix}.zap"
        run_cmd(scr_cmd, session.test_mode)

        #Post scrunching zapping. Will need to be unique per source
        pzap_cmd = f'paz -z "17 36 15 7 2 0 1 5 47 40 34" -e pzap -O {session.output_dir} {session.output_dir}/{prefix}.ftscr'
        run_cmd(pzap_cmd, session.test_mode)


    #Make a metafile of the fully zapped and scrunched files
    metafile_cmd = f'ls {session.output_dir}/{session.datafile_glob_prefix}.pzap > {session.output_dir}/{session.psrname}.meta'
    os.system(metafile_cmd)
    meta_file = f"{session.output_dir}/{session.psrname}.meta"
    #print(meta_file)
    gt = ppt.GetTOAs(meta_file, session.model_portrait)
    gt.get_TOAs(DM0=session.dm)

