#! /usr/bin/env python

import re

# giza a look
from pprint import pprint
    
#info = get_nutrients_per_serving()
fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size']
qry_string = ', '.join(fields)

print 

print(f"SELECT {qry_string} FROM exploded WHERE image_file <> '';")

content = "1401, 'emergency broth', Decimal('13.00'), Decimal('0.71'), Decimal('0.48'), Decimal('0.41'), Decimal('1.30'), Decimal('315.00')"

#m = re.finditer(r"Decimal\('(.*?)'\)", content)
m = re.search(r"Decimal\('(.*?)'\)", content)
#m = re.search(r'Decimal\((.*?)\)', content)

print(type(m))
print("Looking:")
print(content)
print(m.group(0))
print(m.group(1))