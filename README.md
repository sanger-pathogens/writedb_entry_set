# writedb_entry_set

Repo to hold the writedb_entry_set Python code, extracted from the Sanger general GitLab repo.
The main script, writedb_entries.py, provides a wrapper for the Artemis writedb_entry script that is used to extract 
Chado feature data to GFF or EMBL file formats.

[![Build Status](https://travis-ci.org/sanger-pathogens/writedb_entry_set.svg?branch=master)](https://travis-ci.org/sanger-pathogens/writedb_entry_set)   
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/ariba/blob/master/LICENSE)   
[![codecov](https://codecov.io/gh/sanger-pathogens/writedb_entry_set/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/writedb_entry_set)

## Installation

### Required dependencies
  * [Python3](https://www.python.org) version >= 3.6.0

### Install from source
Download the latest release from this github repository or clone it.
```
python3 setup.py install
```

## Usage
```
Usage: writedb_entries.py [options]

Options:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism=ORGANISM
                        the organism common_name (can specify many of these)
  -n ANNOTATED_ONLY, --annotated_only=ANNOTATED_ONLY
                        for the organisms specified with this option, only
                        retrieve top-level features that are deemed to have
                        annotations
  -e, --embl            export in EMBL format (defaults to GFF)
  -p PREFIX, --prefix=PREFIX
                        a prefix to prepend to the export folder name
  -b BUNDLE, --bundle=BUNDLE
                        if you wish to autogenerate a bundle, provide path
                        here
  -w WRITEDB_ENTRY, --writedb_entry=WRITEDB_ENTRY
                        the path to writedb_entry
  -m MAX_FEATURE_INCREMENT, --max_feature_increment=MAX_FEATURE_INCREMENT
                        the max number features to be batched by artemis in
                        one go
  -f MAX_FILES_PER_FOLDER, --max_files_per_folder=MAX_FILES_PER_FOLDER
                        the max number of files per folder
  --single_file         write sorted, postprocessed single GFF file per
                        organism (requires GenomeTools `gt' executable in
                        PATH)
  -v, --verbose         output additional information while running
  -d DATABASE_CONNECTION, --database_connection=DATABASE_CONNECTION
                        either a database uri or a path to a conf_file
  -x EXPORT_FOLDER, --export_folder=EXPORT_FOLDER
                        the path to the destination_folder
  -a, --suffix_date_in_path
                        suffixes the base path with the starting date and time
  -t, --test            add the -test option
  -l, --flattened       if embl, flatten
  -s START_AT_FEATURE_UNIQUENAME, --start_at_feature_uniquename=START_AT_FEATURE_UNIQUENAME
                        start at the feature_id (for resuming stalled exports)
  -z, --emblsubmission  if embl, use submission format
  -i, --ignoreobsolete  do not export obsolete features
  ```
  
 ## License
writedb_entry_set is free software, licensed under [GPLv3](https://github.com/sanger-pathogens/writedb_entry_set/blob/master/LICENSE).
