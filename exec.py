import json
from datetime import datetime
from glob import glob
from os import Popen

from astropy import log

from session import PulsarConfig, Session


def run_cmd(cmd: str, test_mode: bool):
    """Run a shell command using Popen"""
    try:
        log.info(f"RUN $ {cmd}")
        if not test_mode:
            p = Popen(cmd, shell=True)
            p.wait()
            return p.returncode
        return "skip"
    except:
        log.error(f"Error while executing command. cmd :: {cmd}")
        return "error"


def create_metafile(session: Session, pulsar: PulsarConfig):
    """Make a metafile of the fully zapped and scrunched files"""

    pzap_files = glob(f"{session.output_dir}/{pulsar.datafile_glob_prefix}.pzap")
    meta_file = f"{session.output_dir}/{pulsar.name}.meta"

    log.info(f"Creating meta file {meta_file}.")
    with open(meta_file, "w") as metafile:
        for pzap_file in pzap_files:
            metafile.write(f"{pzap_file}\n")

    return meta_file


def create_exec_summary_file(session: Session, exec_summary: dict):
    """Create an execution summary file."""
    now_str = datetime.now().isoformat()
    with open(
        f"{session.output_dir}/chime_pipeline_summary_{now_str}.json", "w"
    ) as summary_file:
        json.dump(exec_summary, summary_file)
