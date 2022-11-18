#!/usr/bin/env python

import os
import traceback

from astropy import log

from chime_pipeline.exec import create_exec_summary_file, run_cmd, update_fits_header
from chime_pipeline.fileutils import (
    get_file_prefix,
    get_final_output_filename,
    get_ftscr_filename,
    get_input_ar_files,
    get_pzap_filename,
    get_zap_filename,
)
from chime_pipeline.session import Session
from chime_pipeline.toautils import create_toas, remove_toa_file, validate_toa_file
from chime_pipeline.validation import test_input_file

if __name__ == "__main__":

    log.setLevel("INFO")

    execution_summary = dict()

    session = Session()

    if session.reprocess:
        log.info("Will reprocess all input files (--reprocess).")

    for pulsar in session.pulsars:

        log.info(f"### Processing {pulsar.name} ###")

        # All input files.
        input_ar_files = get_input_ar_files(session, pulsar)

        # Summary dict.
        execution_summary[pulsar.name] = {
            "num_files_total": len(input_ar_files),
            "num_files_success": 0,
            "num_files_skip_exist": 0,
            "num_files_skip_meta": 0,
            "num_files_processfail": 0,
            "num_files_toafail": 0,
        }

        # List to store successfully processed files for TOA generation.
        input_files_for_toas = []

        # Process files one-by-one to reduce memory issues
        # Skip files that are not processed successfully.
        for ar_file in input_ar_files:
            prefix = get_file_prefix(ar_file)

            # Skip the file if it is not in the input metafile if the input metafile is given.
            if session.input_metafile is not None:
                if ar_file not in session.input_file_names:
                    log.info(
                        f"--- Skipping {prefix} ... Not included in the input metafile. ---"
                    )
                    execution_summary[pulsar.name]["num_files_skip_meta"] += 1
                    continue

            # Skip the file if it has already been processed (except when the --reprocess option is given).
            final_output_file = get_final_output_filename(session, pulsar, prefix)
            if (
                os.path.exists(final_output_file) and os.path.isfile(final_output_file)
            ) and not session.reprocess:
                log.info(f"--- Skipping {prefix} ... Output already exists. ---")
                execution_summary[pulsar.name]["num_files_skip_exist"] += 1
                input_files_for_toas.append(final_output_file)
                continue

            log.info(f"--- Processing {prefix} ---")

            try:
                test_input_file(f"{ar_file}")
            except OSError as err:
                log.error(f"Error reading file {ar_file}. Skipping file.")
                execution_summary[pulsar.name]["num_files_processfail"] += 1
                continue

            # CHIME preprocessing script
            # 1. Convert coherence mode data to Stokes mode.
            # 2. Run RFI excision
            # 3. Convert from Timer to PSRFITS format
            zap_cmd = f"chime_convert_and_tfzap.psh -e zap -O {session.output_dir} {ar_file}"
            run_cmd(zap_cmd, session.test_mode)

            try:
                zap_file = get_zap_filename(session, prefix)
                test_input_file(zap_file)
            except OSError as err:
                log.error(f"Error reading file {zap_file}. Skipping file.")
                execution_summary[pulsar.name]["num_files_processfail"] += 1
                continue

            update_fits_header(zap_file, 1)

            # Scrunch in Frequency and Time, Update DM
            scr_cmd = f"pam -e ftscr -u {session.output_dir} --setnchn {pulsar.nchan} --setnsub {pulsar.nsub} -d {pulsar.dm} {zap_file}"
            run_cmd(scr_cmd, session.test_mode)

            try:
                ftscr_file = get_ftscr_filename(session, prefix)
                test_input_file(ftscr_file)
            except OSError as err:
                log.error(f"Error reading file {ftscr_file}. Skipping file.")
                execution_summary[pulsar.name]["num_files_processfail"] += 1
                continue

            update_fits_header(ftscr_file, 2)

            if session.clean_files:
                log.warning(f"Removing file {zap_file} ... (--clean)")
                os.unlink(zap_file)

            if not session.skip_pzap and len(pulsar.zap_chans) > 0:
                # Remove bad channels based on the config.
                # This will need to be unique for each pulsar.
                zap_chans_str = " ".join(map(str, pulsar.zap_chans))
                pzap_cmd = f'paz -z "{zap_chans_str}" -e pzap -O {session.output_dir} {ftscr_file}'
                run_cmd(pzap_cmd, session.test_mode)

                try:
                    pzap_file = get_pzap_filename(session, prefix)
                    test_input_file(pzap_file)
                except OSError as err:
                    log.error(f"Error reading file {pzap_file}. Skipping file.")
                    execution_summary[pulsar.name]["num_files_processfail"] += 1
                    continue

                update_fits_header(pzap_file, 3)

                # This will change if there are fewer or more steps.
                assert pzap_file == final_output_file

                if session.clean_files:
                    log.warning(f"Removing file {ftscr_file} ... (--clean)")
                    os.unlink(ftscr_file)

            elif len(pulsar.zap_chans) == 0:
                log.warning(
                    "Skipping post-scrunch zapping step because no channels were flagged for zapping (zap_chans)."
                )
                assert ftscr_file == final_output_file
            else:
                log.info("Skipping post-scrunch zapping step. (--skip_pzap)")
                assert ftscr_file == final_output_file

            input_files_for_toas.append(final_output_file)
            execution_summary[pulsar.name]["num_files_success"] += 1

        if not session.skip_toagen and len(pulsar.template) > 0:
            # Recreate the TOA file. Any existing TOA file will be rewritten.
            # Skip files for which the TOA generation fails.
            remove_toa_file(session, pulsar)
            for toa_input_file in input_files_for_toas:
                try:
                    create_toas(session, pulsar, toa_input_file)
                except Exception as err:
                    log.error(
                        f"Failed to create TOA for {toa_input_file}. Skipping file."
                    )
                    log.error(err)
                    traceback.print_tb(err.__traceback__)
                    execution_summary[pulsar.name]["num_files_toafail"] += 1
                    continue

            # Validate TOA file
            # -- Can it be read using PINT?
            # -- Is the number of TOAs equal to the expected number?
            num_toas_expected = (
                execution_summary[pulsar.name]["num_files_total"]
                - execution_summary[pulsar.name]["num_files_skip_meta"]
                - execution_summary[pulsar.name]["num_files_toafail"]
            )
            validate_toa_file(session, pulsar, num_toas_expected)
        elif len(pulsar.template) == 0:
            log.warning(
                "Skipping TOA generation because the template file is not specified."
            )
            # num_files_toafail is not relevant if no TOAs are generated.
            execution_summary[pulsar.name].pop("num_files_toafail")
        else:
            log.info("Skipping TOA generation (--skip_toagen).")
            # num_files_toafail is not relevant if --skip_toagen is given.
            execution_summary[pulsar.name].pop("num_files_toafail")

    # Write out a summary in JSON format.
    create_exec_summary_file(session, execution_summary)
