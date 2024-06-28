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

def sync_files_to_nas(opts={}):
    global opt_dict
    opt_dict.update(opts)    # update the defaults with the passed in options
                                    # then use the updated 

    source_dir = opt_dict['source_dir']
    target_dir = opt_dict['target_dir']

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
    total = len(files_to_copy)
    print(f"Copying . . . {total} files")
    err_count = 0
    err_list = []
    for n,f in enumerate(files_to_copy):
        if opt_dict['verbose_mode']:
            print(f"{n:04}/{total:04}> {f}")
        else:
            print('.', end='')  # show progress
        if opt_dict['live_copy']:
            try:
                shutil.copy2(os.path.join(source_dir, f), target_dir)
            except Exception as e:
                print(f"Error copying {f}:\n{e}")
                err_count += 1
                err_list.append((f,e))

    print(f"\nCopied {len(files_to_copy)} files\n\tfrom {source_dir}\n\t\ to {target_dir}.")
    if err_count:
        print(f"Errors: {err_count}")
        for f,e in err_list:
            print(f"\t{f}:\n\t{e}")


if __name__ == '__main__':
    sync_files_to_nas(opt_dict)
    sync_files_to_nas({'live_copy':True,'verbose_mode':True})
    # TODO merge options passed in with defaults
    #sync_files_to_nas({'verbose_mode':opt_dict['verbose_mode']})
    if opt_dict['live_copy']:
        print("Done.")
    else:
        print(help_string)
    sys.exit(0)