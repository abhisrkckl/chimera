import os

from loguru import logger as log
from pint.toa import get_TOAs
from pplib import write_TOAs
from pptoas import GetTOAs

from .session import PulsarConfig, Session


def get_tim_filename(session: Session, pulsar: PulsarConfig):
    return f"{session.output_dir}/{pulsar.name}.tim"


def create_toas(session: Session, pulsar: PulsarConfig, input_file: str):
    # Make a metafile of the fully zapped and scrunched files
    # session.create_output_metafile(pulsar)

    gt = GetTOAs(input_file, pulsar.template)
    gt.get_TOAs(DM0=pulsar.dm)

    # Writing to a tim file
    # There is an optional SNR_cutoff and way to append to an existing timfile
    timfile = get_tim_filename(session, pulsar)
    write_TOAs(gt.TOA_list, SNR_cutoff=0.0, outfile=timfile, append=True)


def remove_toa_file(session: Session, pulsar: PulsarConfig):
    timfile = get_tim_filename(session, pulsar)
    if os.path.isfile(timfile):
        log.info(f"File {timfile} will be rewritten.")
        os.unlink(timfile)


def validate_toa_file(session: Session, pulsar: PulsarConfig, num_toas_expected: int):
    timfile = get_tim_filename(session, pulsar)
    try:
        toas = get_TOAs(timfile)
        assert len(toas) == num_toas_expected
        log.info(f"Successfully created {timfile}.")
    except:
        log.error(f"Unable to validate {timfile}.")
