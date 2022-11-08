#!/usr/bin/env python

import glob
import os
from astropy import log
from pplib import *
import pptoas as ppt
import subprocess
import argparse
import json
from tests import test_dir, test_input_file, test_read_dir

log.setLevel("INFO")


class PulsarConfig:
    def __init__(
        self,
        name: str,
        dm: float,
        model_portrait: str,
        nchan: int,
        nsub: int,
        zap_chans: str,
    ):
        self.name = name
        self.dm = dm
        self.model_portrait = model_portrait
        self.nchan = nchan
        self.nsub = nsub
        self.zap_chans = zap_chans
        self.datafile_glob_prefix = f"CHIME_{self.name}_beam_?_?????_?????"


class Session:
    """Class for storing command line arguments and other global state."""

    def __init__(self):

        parser = argparse.ArgumentParser(
            description="Generate TOAs from fold mode CHIME data."
        )
        parser.add_argument(
            "-i",
            "--input_dir",
            required=True,
            help="Directory where input archives are stored.",
        )
        parser.add_argument(
            "-o",
            "--output_dir",
            required=True,
            help="Directory where output files will be stored.",
        )
        parser.add_argument(
            "-c", "--config", required=True, help="Configuration file (JSON format)."
        )
        parser.add_argument(
            "-t",
            "--test",
            required=False,
            dest="test_mode",
            action="store_true",
            help="Run in test mode (don't execute commands, display only).",
        )
        args = parser.parse_args()

        self.input_dir = test_read_dir( os.path.realpath(args.input_dir) )
        self.output_dir = test_dir( os.path.realpath(args.output_dir) )
        self.config_file = test_input_file( os.path.realpath(args.config) )
        
        self.test_mode = args.test_mode

        self.process_config()

    def process_config(self):
        with open(self.config_file, "r") as cf:
            try:
                config_data = json.load(cf)
                self.pulsars = [PulsarConfig(**psr_data) for psr_data in config_data]
            except:
                raise AttributeError(
                    "The JSON config is malformed or missing attributes."
                )


def run_cmd(cmd: str, test_mode: bool):
    """Run a shell command using Popen"""
    try:
        log.info(cmd)
        if not test_mode:
            p = subprocess.Popen(cmd, shell=True)
            p.wait()
    except:
        raise OSError(f"Error while executing command.\ncmd :: {cmd}")


def create_metafile(session: Session, pulsar: PulsarConfig):
    """Make a metafile of the fully zapped and scrunched files"""

    pzap_files = glob.glob(f"{session.output_dir}/{pulsar.datafile_glob_prefix}.pzap")
    meta_file = f"{session.output_dir}/{pulsar.name}.meta"

    log.info(f"Creating meta file {meta_file}.")
    with open(meta_file, "w") as metafile:
        for pzap_file in pzap_files:
            metafile.write(f"{pzap_file}\n")

    return meta_file


if __name__ == "__main__":

    session = Session()
    for pulsar in session.pulsars:
        log.info(f"### Processing {pulsar.name} ###")

        # Run psrsh in a loop to avoid memory issues
        input_ar_files = glob.glob(
            f"{session.input_dir}/{pulsar.datafile_glob_prefix}.ar"
        )
        for ar_file in input_ar_files:
            prefix = os.path.splitext(os.path.basename(ar_file))[0]

            # Skip processing the file if it has already been processed.
            final_output_file = f"{session.output_dir}/{prefix}.pzap"
            if os.path.exists(final_output_file):
                log.info(f"--- Skipping {prefix} ... Output already exists. ---")
                continue

            log.info(f"--- Processing {prefix} ---")

            zap_cmd = f"psrsh chime_convert_and_tfzap.psh -e zap -O {session.output_dir} {session.input_dir}/{prefix}.ar"
            run_cmd(zap_cmd, session.test_mode)

            # Command to scrunch to 64 frequency channels
            scr_cmd = f"pam -e ftscr -u {session.output_dir} --setnchn {pulsar.nchan} --setnsub {pulsar.nsub} -d {pulsar.dm} {session.output_dir}/{prefix}.zap"
            run_cmd(scr_cmd, session.test_mode)

            # Post scrunching zapping. Will need to be unique per source
            pzap_cmd = f'paz -z "{pulsar.zap_chans}" -e pzap -O {session.output_dir} {session.output_dir}/{prefix}.ftscr'
            run_cmd(pzap_cmd, session.test_mode)

        # Make a metafile of the fully zapped and scrunched files
        meta_file = create_metafile(session, pulsar)

        gt = ppt.GetTOAs(meta_file, pulsar.model_portrait)
        gt.get_TOAs(DM0=pulsar.dm)
        # Writing to a tim file
        timfile = f"{session.output_dir}/{pulsar.name}.tim"
        # There is an optional SNR_cutoff and way to append to an existing timfile
        write_TOAs(gt.TOA_list, SNR_cutoff=0.0, outfile=timfile, append=False)
