#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path

__iface_files = {}

config_file = './scratch/config_files.json'
with open(config_file, 'r') as f:
    json_config = f.read()
    __iface_files = json.loads(json_config)
    print(f"Config files LOADED ({__iface_files.__len__()})")


def get_file_for_data_set(data_set):
    if data_set in __iface_files:
        database_file = Path(__iface_files[data_set])
    else:
        raise(f"DATABASE stub ERROR: KeyError data_set key <{data_set}> doesn't exist")    

    return database_file


if __name__ == '__main__':
    from pathlib import Path
    # https://docs.python.org/3/library/pathlib.html#basic-use
    
    for key in __iface_files:
        file_info = Path(__iface_files[key])
        # Path - examples
        # print(f"anchor: {file_info.anchor}")      #
        # print(f"parent:{file_info.parent}")       # path
        # print(f"stem: {file_info.stem}")          # basename no ext
        # print(f"suffix: {file_info.suffix}")      # ext
        # print(f"suffixes: {file_info.suffixes}")  # .tar.gz  < both as array
        # print(f"as_uri: {file_info.as_uri}")        
        # print(f"K:{key} \t\t{file_info.name} \t{file_info.stem}") # name > basename.ext
    
    print(f"join: { Path(__iface_files['archive_path']).joinpath( Path(__iface_files['user_database']).name ) }")