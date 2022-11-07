# chime_pipeline
Create wideband TOAs from CHIME pulsar observations (fold mode data).

## Usage

`chime_pipeline.py [-h] -i INPUT_DIR -o OUPUT_DIR -c CONFIG [-t]`

| Option                                    | Description                                               |  
|-------------------------------------------|-----------------------------------------------------------|
| `-h`, `--help`                            | Show this help message and exit                           |
| `-i INPUT_DIR`, `--input_dir INPUT_DIR`   | Directory where input archives are stored.                |
| `-o OUPUT_DIR`, `--ouput_dir OUPUT_DIR`   | Directory where output files will be stored.              |
| `-c CONFIG`, `--config CONFIG`            | Configuration file (JSON format).                         |
| `-t`, `--test`                            | Run in test mode (don't execute commands, display only).  |
|-------------------------------------------|-----------------------------------------------------------|