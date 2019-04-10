#!/usr/bin/env python

import sys
import os

from pprint import pprint

with open('./env_var_script_output.txt', 'w') as env_file:
        
        for paths in sys.path:
                print(f"{paths}")
                env_file.write(f"{paths}\n")
        
        #print "%20s %s" % (k,v)
        for k,v in os.environ.items():
                print(f"{k} - {v}")
                env_file.write(f"{k} - {v}\n")
