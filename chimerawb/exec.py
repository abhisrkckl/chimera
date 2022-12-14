import json
from subprocess import Popen, check_output
import sys
import time

from loguru import logger as log
from astropy.io import fits

from .session import Session


def run_cmd(cmd: str, test_mode: bool):
    """Run a shell command using Popen"""
    try:
        log.info(f"RUN $ {cmd}")
        if not test_mode:
            start = time.time()
            p = Popen(cmd, shell=True)
            p.wait()
            end = time.time()
            return p.returncode, end - start
        return "skip"
    except:
        log.error(f"Error while executing command. cmd :: {cmd}")
        return "error"


def create_exec_summary_file(session: Session, exec_summary: dict):
    """Create an execution summary file."""
    with open(f"{session.output_dir}/chime_pipeline_summary.json", "w") as summary_file:
        json.dump(exec_summary, summary_file, indent=4)


def update_fits_header(filename: str, level: int):
    try:
        cmd = " ".join(sys.argv)
        fits.setval(filename, "PL_CMD", value=cmd)
        fits.setval(filename, "PL_LVL", value=level)
        log.info(f"Updated FITS header for {filename}.")
    except:
        log.error(f"Failed to update FITS header for {filename}.")


def get_psrchive_version():
    try:
        return (
            check_output(["psrchive", "--version"])
            .decode("utf-8")
            .strip()[len("psrchive ") :]
        )
    except:
        log.warning("Unable to get PSRCHIVE version.")
        return "Unknown"
