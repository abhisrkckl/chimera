import argparse
import os
import json
from validation import test_dir, test_input_file, test_read_dir


class PulsarConfig:
    def __init__(
        self,
        name: str,
        dm: float,
        model_portrait: str,
        nchan: int,
        nsub: int,
        zap_chans: str,
    ):
        self.name = name
        self.dm = dm
        self.model_portrait = model_portrait
        self.nchan = nchan
        self.nsub = nsub
        self.zap_chans = zap_chans
        self.datafile_glob_prefix = f"CHIME_{self.name}_beam_?_?????_?????"


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
            "-o",
            "--output_dir",
            required=True,
            help="Directory where output files will be stored.",
        )
        parser.add_argument(
            "-c", "--config", required=True, help="Configuration file (JSON format)."
        )
        parser.add_argument(
            "-t",
            "--test",
            required=False,
            dest="test_mode",
            action="store_true",
            help="Run in test mode (don't execute commands, display only).",
        )
        args = parser.parse_args()

        self.input_dir = test_read_dir(os.path.realpath(args.input_dir))
        self.output_dir = test_dir(os.path.realpath(args.output_dir))
        self.config_file = test_input_file(os.path.realpath(args.config))

        self.test_mode = args.test_mode

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
