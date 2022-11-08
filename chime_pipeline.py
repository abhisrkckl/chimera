#!/usr/bin/env python

import os

from astropy import log

from exec import create_exec_summary_file, run_cmd
from fileutils import get_file_prefix, get_final_output_file, get_input_ar_files
from session import Session
from toautils import create_tim_file
from validation import test_input_file

if __name__ == "__main__":

    log.setLevel("INFO")

    execution_summary = dict()

    session = Session()
    for pulsar in session.pulsars:

        log.info(f"### Processing {pulsar.name} ###")

        # Run psrsh in a loop to avoid memory issues
        input_ar_files = get_input_ar_files(session, pulsar)

        execution_summary[pulsar.name] = {
            "num_files_total": len(input_ar_files),
            "num_files_success": 0,
            "num_files_skip_exist": 0,
            "num_files_skip_meta": 0,
        }

        for ar_file in input_ar_files:
            prefix = get_file_prefix(ar_file)

            # Skip the file if it is not in the input metafile (if input metafile is given).
            if session.input_metafile is not None:
                print(session.input_file_names)
                if ar_file not in session.input_file_names:
                    log.info(f"--- Skipping {prefix} ... Not incuded in the input metafile. ---")
                    execution_summary[pulsar.name]["num_files_skip_meta"] += 1
                    continue

            # Skip the file if it has already been processed.
            final_output_file = get_final_output_file(session, prefix)
            if os.path.exists(final_output_file) and os.path.isfile(final_output_file):
                log.info(f"--- Skipping {prefix} ... Output already exists. ---")
                execution_summary[pulsar.name]["num_files_skip_exist"] += 1
                continue

            log.info(f"--- Processing {prefix} ---")

            try:
                test_input_file(f"{ar_file}")
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

        if execution_summary[pulsar.name]["num_files_success"] > 0:
            create_tim_file(session, pulsar)
        else:
            log.warning("Skipping TOA file creation as no new files were processed.")

    create_exec_summary_file(session, execution_summary)
