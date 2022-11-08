#!/usr/bin/env python

import glob
import os

from astropy import log
from pplib import write_TOAs
from pptoas import GetTOAs

from exec import create_exec_summary_file, create_metafile, run_cmd
from session import Session
from validation import test_input_file

log.setLevel("INFO")


if __name__ == "__main__":

    execution_summary = dict()

    session = Session()
    for pulsar in session.pulsars:

        log.info(f"### Processing {pulsar.name} ###")

        # Run psrsh in a loop to avoid memory issues
        input_ar_files = glob.glob(
            f"{session.input_dir}/{pulsar.datafile_glob_prefix}.ar"
        )

        execution_summary[pulsar.name] = {
            "num_files_total": len(input_ar_files),
            "num_files_success": 0,
            "num_files_skip_exist": 0,
        }

        for ar_file in input_ar_files:
            prefix = os.path.splitext(os.path.basename(ar_file))[0]

            # Skip processing the file if it has already been processed.
            final_output_file = f"{session.output_dir}/{prefix}.pzap"
            if os.path.exists(final_output_file):
                log.info(f"--- Skipping {prefix} ... Output already exists. ---")
                execution_summary[pulsar.name]["num_files_skip_exist"] += 1
                continue

            log.info(f"--- Processing {prefix} ---")

            try:
                test_input_file(f"{session.input_dir}/{prefix}.ar")
            except OSError as err:
                log.error(
                    f"Error reading file {session.input_dir}/{prefix}.ar. Skipping file."
                )
                continue

            # CHIME preprocessing script
            zap_cmd = f"psrsh chime_convert_and_tfzap.psh -e zap -O {session.output_dir} {session.input_dir}/{prefix}.ar"
            run_cmd(zap_cmd, session.test_mode)

            try:
                test_input_file(f"{session.output_dir}/{prefix}.zap")
            except OSError as err:
                log.error(
                    f"Error reading file {session.output_dir}/{prefix}.zap. Skipping file."
                )
                continue

            # Command to scrunch to 64 frequency channels
            scr_cmd = f"pam -e ftscr -u {session.output_dir} --setnchn {pulsar.nchan} --setnsub {pulsar.nsub} -d {pulsar.dm} {session.output_dir}/{prefix}.zap"
            run_cmd(scr_cmd, session.test_mode)

            try:
                test_input_file(f"{session.output_dir}/{prefix}.ftscr")
            except OSError as err:
                log.error(
                    f"Error reading file {session.output_dir}/{prefix}.ftscr. Skipping file."
                )
                continue

            # Post scrunching zapping. Will need to be unique per source
            pzap_cmd = f'paz -z "{pulsar.zap_chans}" -e pzap -O {session.output_dir} {session.output_dir}/{prefix}.ftscr'
            run_cmd(pzap_cmd, session.test_mode)

            try:
                test_input_file(f"{session.output_dir}/{prefix}.pzap")
            except OSError as err:
                log.error(
                    f"Error reading file {session.output_dir}/{prefix}.pzap. Skipping file."
                )
                continue

            execution_summary[pulsar.name]["num_files_success"] += 1

        # Make a metafile of the fully zapped and scrunched files
        meta_file = create_metafile(session, pulsar)

        gt = GetTOAs(meta_file, pulsar.model_portrait)
        gt.get_TOAs(DM0=pulsar.dm)
        # Writing to a tim file
        timfile = f"{session.output_dir}/{pulsar.name}.tim"
        # There is an optional SNR_cutoff and way to append to an existing timfile
        write_TOAs(gt.TOA_list, SNR_cutoff=0.0, outfile=timfile, append=False)

    create_exec_summary_file(session, execution_summary)
