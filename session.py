import argparse
import json
import os
from glob import glob

from astropy import log

from validation import test_dir, test_input_file, test_read_dir


class PulsarConfig:
    def __init__(
        self,
        name: str,
        dm: float,
        template: str,
        nchan: int,
        nsub: int,
        zap_chans: list,
    ):
        self.name = name
        self.dm = dm
        self.template = test_input_file(template)
        self.nchan = nchan
        self.nsub = nsub
        self.zap_chans = zap_chans
        self.datafile_glob_prefix = f"CHIME_{self.name}_beam_?_?????_?????"

        self.validate()

    def validate(self):
        try:
            assert isinstance(self.name, str) and len(self.name) > 0
            assert isinstance(self.dm, float) and self.dm > 0
            assert isinstance(self.template, str)
            assert isinstance(self.nchan, int) and self.nchan > 0
            assert isinstance(self.nsub, int) and self.nchan > 0
            assert isinstance(self.zap_chans, list)

            for zap_chan in self.zap_chans:
                assert (
                    isinstance(zap_chan, int)
                    and zap_chan >= 0
                    and zap_chan <= self.nchan
                )
        except:
            log.error("Unable to validate the config.")
            raise

        log.info("Successfully validated the config.")


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
            "-m",
            "--metafile",
            required=False,
            help="Meta file that lists the input archives (input files should be stored in input_dir).",
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
        # parser.add_argument(
        #     "-t",
        #     "--test",
        #     required=False,
        #     dest="test_mode",
        #     action="store_true",
        #     help="Run in test mode (don't execute commands, display only).",
        # )
        parser.add_argument(
            "-r",
            "--reprocess",
            required=False,
            dest="reprocess",
            action="store_true",
            help="Reprocess files regardless of existing output files.",
        )
        parser.add_argument(
            "--skip_pzap",
            required=False,
            dest="skip_pzap",
            action="store_true",
            help="Skip post-scrunch RFI zapping step.",
        )
        args = parser.parse_args()

        self.input_dir = test_read_dir(os.path.realpath(args.input_dir))
        self.output_dir = test_dir(os.path.realpath(args.output_dir))
        self.config_file = test_input_file(os.path.realpath(args.config))

        if args.metafile is not None:
            self.input_metafile = test_input_file(os.path.realpath(args.metafile))
            with open(self.input_metafile, "r") as metafile:
                self.input_file_names = []
                for f in metafile.readlines():
                    f_full = test_input_file(f"{self.input_dir}/{f.strip()}")
                    self.input_file_names.append(f_full)
        else:
            self.input_metafile = None

        self.test_mode = False  # args.test_mode
        self.reprocess = args.reprocess
        self.skip_pzap = args.skip_pzap

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

    def create_output_metafile(self, pulsar: PulsarConfig):
        """Make a metafile of the fully zapped and scrunched files"""

        pzap_files = glob(f"{self.output_dir}/{pulsar.datafile_glob_prefix}.pzap")
        output_meta_file = f"{self.output_dir}/{pulsar.name}.meta"

        log.info(f"Creating meta file {output_meta_file}.")
        with open(output_meta_file, "w") as metafile:
            for pzap_file in pzap_files:
                metafile.write(f"{pzap_file}\n")

        self.output_meta_file = output_meta_file
