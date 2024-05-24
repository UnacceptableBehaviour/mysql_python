#! /usr/bin/env python

import sys

opt_dict = {
    'verbose_mode':     False,
    'live_copy':        False,  # Set to True to actually copy files
    'source_dir':       "/Users/simon/a_syllabus/lang/python/asset_server/static/recipe",
    'target_dir':       "/Volumes/docker/dtk-swarm-2/asset_server/static/recipe",
}

if '-v' in sys.argv:
    opt_dict['verbose_mode'] = True

if '-go' in sys.argv:
    opt_dict['live_copy'] = True

help_string = f'''\n\n\n
HELP:\n
Scan NAS for missing assets & copy over

EG ./synch_assets_to_nas.py -v -go      # Verbose mode, go ahead and copy files

- - - options - - - 
-v          Verbose mode turn on more diagnostics
-go         Go ahead and copy files

-h          This help
'''

if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
    print(help_string)
    sys.exit(0)

import os
import shutil

def sync_files_to_nas(opts=opt_dict):
    source_dir = opts['source_dir']
    target_dir = opts['target_dir']

    # Check if target directory is mounted
    while not os.path.isdir(target_dir):
        input(f"The directory {target_dir} is not mounted. Press Enter to check again...")

    # Get list of image and txt files in source directory
    source_files = [f for f in os.listdir(source_dir) if (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.txt'))]

    # Get list of image and txt files in target directory
    target_files = [f for f in os.listdir(target_dir) if (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.txt'))]

    # Find files that are in source directory but not in target directory
    files_to_copy = [f for f in source_files if f not in target_files]

    # Copy these files to target directory
    print(f"Copying . . .")
    for f in files_to_copy:
        if opts['verbose_mode']:
            print(f"> {f}")
        if opts['live_copy']:
            shutil.copy2(os.path.join(source_dir, f), target_dir)
            pass

    print(f"\nCopied {len(files_to_copy)} files\n\tfrom {source_dir}\n\t\ to {target_dir}.")


if __name__ == '__main__':
    #sync_files_to_nas(opt_dict)
    sync_files_to_nas({'verbose_mode':opt_dict['verbose_mode']})
    print("Done.")
    sys.exit(0)