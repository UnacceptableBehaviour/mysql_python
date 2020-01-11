#! /usr/bin/env python

import re

# giza a look
from pprint import pprint
    
#info = get_nutrients_per_serving()
fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size']
qry_string = ', '.join(fields)


print(f"SELECT {qry_string} FROM exploded WHERE lead_image <> '';")

content = "1401, 'emergency broth', Decimal('13.00'), Decimal('0.71'), Decimal('0.48'), Decimal('0.41'), Decimal('1.30'), Decimal('315.00')"

#m = re.finditer(r"Decimal\('(.*?)'\)", content)
m = re.search(r"Decimal\('(.*?)'\)", content)
#m = re.search(r'Decimal\((.*?)\)', content)

print(type(m))
print("Looking:")
print(content)
print(m.group(0))
print(m.group(1))


allergens = 'dairy, eggs, peanuts, nuts, seeds, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur dioxide'
tags = 'vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant'


print("List comprehension test")
for a in allergens.split(','):
  print(a.strip())
  
l_c = [ a.strip() for a in allergens.split(',') ]  
pprint(l_c)


txt = f"allergens: {allergens}\ntags: {tags}\n"
match = re.search( r'^allergens:(.*?)$.*?tags:(.*?)$', txt, re.MULTILINE | re.DOTALL )

pprint(match.groups)
print(match.groups)

# create tag & allergens entries, populate them if they exist
recipe_info = {}
recipe_info['allergens'] = [ a.strip() for a in match.group(1).split(',') ]
recipe_info['tags'] = [ a.strip() for a in match.group(2).split(',') ]

pprint(recipe_info)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# upload support - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# upload support - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

fnames = ['.bashrc','ck.sre', 'double.jpg.monkey','double.monkey.jpg','imageone.jpg','hoot.txt','badboy_bubba']

for f in fnames:
  print("> - - \ ")
  print(allowed_file(f))
  print('.' in f)
  if ('.' in f):
    print(f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    print(f.rsplit('.', 1))
    print(f.rsplit('.', 1)[1])
  print("> - - / ")
