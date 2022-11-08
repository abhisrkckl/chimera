import os
from loguru import logger

def test_read_dir(folder, ok=True):
    if not os.access(folder, os.F_OK):
        raise OSError(f"{folder} does not exist.")
    elif not os.path.isdir(folder):
        raise OSError(f"{folder} is not a directory.")
    elif not os.access(folder, os.R_OK):
        raise OSError(f"{folder} not readable.")
    elif ok:
        logger.info(f"Directory {folder} OK. ")
    
    return folder

def test_dir(folder, ok=True):
    test_read_dir(folder, ok=False)
    if not os.access(folder, os.W_OK):
        raise OSError(f"{folder} not writable.")
    elif ok:
        logger.info(f"Directory {folder} OK. ")
    
    return folder

def test_input_file(file_path, ok=True):
    if not os.access(file_path, os.F_OK):
        raise OSError(f"{file_path} does not exist.")
    elif not os.path.isfile(file_path):
        raise OSError(f"{file_path} is not a file.")
    elif not os.access(file_path, os.R_OK):
        raise OSError(f"{file_path} not readable.")
    else:
        logger.info(f"Input file {file_path} OK. ")
    
    return file_path
