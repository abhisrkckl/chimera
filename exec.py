import json
from subprocess import Popen

from astropy import log

from session import Session


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


def create_exec_summary_file(session: Session, exec_summary: dict):
    """Create an execution summary file."""
    with open(f"{session.output_dir}/chime_pipeline_summary.json", "w") as summary_file:
        json.dump(exec_summary, summary_file)
