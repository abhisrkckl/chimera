# chimera
Create wideband TOAs from CHIME pulsar observations (fold mode data). CHIMERA stands for The CHIME Reduction Algorithm.

## Usage

    $ chimerawb [-h] -i INPUT_DIR [-m METAFILE] -o OUTPUT_DIR -c CONFIG [-r] [--skip_pzap] [--skip_toagen] [-C]

| Option                                    | Description                                                   |  
|-------------------------------------------|---------------------------------------------------------------|
| `-h`, `--help`                            | Show a help message and exit                                  |
| `-i INPUT_DIR`, `--input_dir INPUT_DIR`   | Directory where input archives are stored.                    |
| `-m METAFILE`, `--metafile METAFILE`      | If given, only process the input files included in METAFILE.  |
| `-o OUTPUT_DIR`, `--output_dir OUTPUT_DIR`| Directory where output files will be stored.                  |
| `-c CONFIG`, `--config CONFIG`            | Configuration file (JSON format).                             |
| `-r`, `--reprocess`                       | Reprocess files regardless of existing output files.          |
| `--skip_pzap`                             | Skip post-scrunch RFI zapping step.                           |
| `--skip_toagen`                           | Skip TOA generation.                                          |
| `-C`, `--clean`                           | Remove intermediate files.                                    |

## Summary

This pipeline takes CHIME fold mode Timer archives as input and produces wide-band TOAs.
The processing steps are as follows:

- If the input metafile is given, only the files listed there will be processed. Otherwise, all files present in the input dir will be processed.
- For each input data file:
    - try
        - Convert coherence mode data to Stokes mode.
        - Run RFI excision
        - Convert from Timer to PSRFITS format
        - Scrunch in Frequency and Time, Update DM (Based on the config file)
        - if not --skip_pzap and zap_chans are given in config file
            - Remove bad channels (Defined in the config file)
    - If any of the above processing steps are unsuccessful, skip that file and proceed.
- if not --skip_toagen and the template is given in the config file
    - Create TOA file from successfully processed data files. (Skip files if TOA generation fails.)
    - Validate TOA file.

## Dependencies

- PSRCHIVE
- PulsePortraiture
- PINT
- astropy
- loguru

## Installation

1. Install `astropy`, `loguru` and `PINT`
    
    `$ pip install astropy loguru pint-pulsar`

2. Install `psrchive` (See https://psrchive.sourceforge.net/download.shtml for instructions)

3. Install `PulsePortraiture`
    
    `$ pip install git+https://github.com/pennucci/PulsePortraiture.git`

4. Install `chimera`    

    `$ pip install git+https://github.com/abhisrkckl/chimera.git`

