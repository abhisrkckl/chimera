# chime_pipeline
Create wideband TOAs from CHIME pulsar observations (fold mode data).

## Usage

`chime_pipeline.py [-h] -i INPUT_DIR -o OUTPUT_DIR -c CONFIG [-t]`

| Option                                    | Description                                               |  
|-------------------------------------------|-----------------------------------------------------------|
| `-h`, `--help`                            | Show a help message and exit                              |
| `-i INPUT_DIR`, `--input_dir INPUT_DIR`   | Directory where input archives are stored.                |
| `-o OUTPUT_DIR`, `--output_dir OUTPUT_DIR`| Directory where output files will be stored.              |
| `-c CONFIG`, `--config CONFIG`            | Configuration file (JSON format).                         |
| `-t`, `--test`                            | Run in test mode (don't execute commands, display only).  |
