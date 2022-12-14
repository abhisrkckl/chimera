19 Sep 2022
 - Initial commit (Code from Lulu)

06 Oct 2022
 - Preliminary pipeline

13 Oct 2022
 - Session class for storing global state
 - run_cmd function
 - Process files one-by-one (Takes up too much memory otherwise)
 - Popen instead of os.system
 - Command line arguments and config file
 - Added license

27 Oct 2022
 - Minor bug fixes
 - Save TOAs to tim file

07 Nov 2022
 - Catch JSON errors
 - Update README

08 Nov 2022
 - Skip already processed files
 - Validation tests for input files and directories
 - Validation tests for intermediate files
 - Rearrange code into multiple files
 - Input metafile
 - Improve logging

09 Nov 2022
 - Create TOAs one by one (better error handling)
 - Remove test mode temporarily (it was broken)
 - Reprocess all input files with `--reprocess` option
 - Validate final output and TOA file
 - Validate config
 - zap_chans in the config file should be a list instead of string.
 - Update README
 - Created CHANGELOG

10 Nov 2022
 - Rename "model_portrait" to "template"
 - Skip post-scrunch zapping with `--skip_pzap` option
 - Skip TOA generation with `--skip_toagen` option
 - Skip TOA generation if template is not given.
 - Skip post-scrunch zapping if no channels are flagged (zap_chans)
 - `--clean` option to remove intermediate files.
 - Update FITS headers (PL_CMD and PL_LVL)

 18 Nov 2022
 - Convert into an installable python package.
 - Use loguru instead of astropy.logging 
 - More information in summary file
 - Rename package to chimera-pulsar and script to chimerawb
 - Check required commands before starting the processing
 - Added installation instructions

30 Nov 2020
 - Changed datafile prefix to be more general
