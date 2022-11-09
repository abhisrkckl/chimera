# chime_pipeline
Create wideband TOAs from CHIME pulsar observations (fold mode data).

## Usage

`chime_pipeline.py [-h] -i INPUT_DIR [-m METAFILE] -o OUTPUT_DIR -c CONFIG [-t] [-r]`

| Option                                    | Description                                                   |  
|-------------------------------------------|---------------------------------------------------------------|
| `-h`, `--help`                            | Show a help message and exit                                  |
| `-i INPUT_DIR`, `--input_dir INPUT_DIR`   | Directory where input archives are stored.                    |
| `-m METAFILE`, `--metafile METAFILE`      | If given, only process the input files included in METAFILE.  |
| `-o OUTPUT_DIR`, `--output_dir OUTPUT_DIR`| Directory where output files will be stored.                  |
| `-c CONFIG`, `--config CONFIG`            | Configuration file (JSON format).                             |
| `-t`, `--test`                            | Run in test mode (don't execute commands, display only).      |
| `-r`, `--reprocess`                       | Reprocess files regardless of existing output files.          |

## Summary

This pipeline takes CHIME fold mode Timer archives as input and produces wide-band TOAs.
The processing steps are as follows:

- If the input metafile is given, only the files listed there will be processed. Otherwise, all files present in the input dir will be processed.
- For each input data file:
    - try
        - Convert coherence mode data to Stokes mode.
        - Run RFI excition
        - Convert from Timer to PSRFITS format
        - Scrunch in Frequency and Time, Update DM (Based on the config file)
        - Remove bad channels (Defined in the config file)
    - If any of the above processing steps are unsuccessful, skip that file and proceed.
- Create TOA file from successfully processed data files. (Skip files if TOA generation fails.)
- Validate TOA file.

## Dependencies

- PSRCHIVE
- PulsePortraiture
- PINT
- astropy
