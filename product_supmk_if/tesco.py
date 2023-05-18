#! /usr/bin/env python

import re
#import sys
#import itertools
from pprint import pprint, pformat
#from pathlib import Path


# Using Tesco API python wrapper
# https://github.com/pbexe/tesco
# pip install tesco
#
# ruby wrapper
# https://github.com/jphastings/TescoGroceries
# https://secure.techfortesco.com/tescoapiweb/ NO work?
#
# https://techfortesco.com/ API?



from tesco import Tesco
from pprint import pprint

t = Tesco("API KEY")
results = t.grocery_search("black turtle beans", offset=0, limit=100)

info = t.product_data(tpnc=results[0]["id"])

pprint(info)
