from pplib import write_TOAs
from pptoas import GetTOAs

from session import PulsarConfig, Session


def create_tim_file(session: Session, pulsar: PulsarConfig):
    # Make a metafile of the fully zapped and scrunched files
    session.create_output_metafile(pulsar)

    gt = GetTOAs(session.output_meta_file, pulsar.model_portrait)
    gt.get_TOAs(DM0=pulsar.dm)
    # Writing to a tim file
    timfile = f"{session.output_dir}/{pulsar.name}.tim"
    # There is an optional SNR_cutoff and way to append to an existing timfile
    write_TOAs(gt.TOA_list, SNR_cutoff=0.0, outfile=timfile, append=False)
