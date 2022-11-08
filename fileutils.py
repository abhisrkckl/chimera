import os
from glob import glob

from session import PulsarConfig, Session


def get_input_ar_files(session: Session, pulsar: PulsarConfig):
    return glob(f"{session.input_dir}/{pulsar.datafile_glob_prefix}.ar")


def get_file_prefix(filename: str):
    return os.path.splitext(os.path.basename(filename))[0]


def get_final_output_file(session: Session, prefix: str):
    return f"{session.output_dir}/{prefix}.pzap"