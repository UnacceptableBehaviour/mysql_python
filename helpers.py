#! /usr/bin/env python

# helper functions

import csv
import itertools
import re
from pathlib import Path

from pprint import pprint # giza a look

# serve files from http://192.168.0.8:8000/static/sql_recipe_data.csv
# $ cd /a_syllabus/lang/python/repos/assest_server 
# $ http-server -p 8000 --cors 
import urllib.request
# urllib.request.urlretrieve ("http://192.168.0.8:8000/static/sql_recipe_data.csv", "sql_recipe_data.csv")
# url = urllib.parse.quote(url, safe='/:')  # make sure files w/ spaces OK

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# load a csv file into a list of dictionaries
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_csv_from_server_as_disctionary(force_reload=False):
    url = 'http://192.168.0.8:8000/static/sql_recipe_data.csv'       
    print("----- get_csv_from_server_as_disctionary -----------------------------------")    
    
    url = urllib.parse.quote(url, safe='/:')  # replace spaces if there are any - urlencode
    print(url)
    
    csv_file = url.split('/')[-1]    
    print(csv_file)
    
    local_file_name = f"./scratch/{csv_file}"

    urllib.request.urlretrieve(url, local_file_name)

    sql_dict = {}

    with open(local_file_name) as csv_to_sql_file:    
        csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
        
        entry = {}
    
        entries = 0
        
        for row in csv_reader:
            entry = {}                          # create a new dictionary for each entry
            
            for col_key in csv_reader.fieldnames:                
                entry[col_key] = row[col_key]   # create and info dictionary    
    
            sql_dict[entries] = entry
            
            entries +=1

    pprint(sql_dict[23])
    
    print("----- reponse ------------------------------------------------------------")
    print(sql_dict.__class__.__name__)
    print(type(sql_dict))
    print(f"ENTRIES: {len(sql_dict)} 0-{len(sql_dict)-1}")
    print(f">---------------------------------------- DICTIONARY LOADED >------------")

    return sql_dict
    

def log_exception(message, exception):
    print("------ caught exception rectrieving url - - - - - - < S")
    print(f"NOTE:{message}\n")
    print(exception)
    f = open('./scratch/error_log.txt', 'a')
    f.write(f"\n\nNOTE: {message} <\n{exception}")
    f.close()
    print("------ caught exception rectrieving url - - - - - - < E")
    return 0

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# load a text file from server - convert into partial recipe dictionary
#                              - ingredients, yield & servings
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_recipe_ingredients_and_yield(recipe_text_filename, recipe_name):    
    recipe_info = {}
    
    print("----- get_recipe_ingredients_and_yield -------------------------------------------------")
    base_url = 'http://192.168.0.8:8000/static/recipe/'
    url = f"{base_url}{recipe_text_filename}"
    print(url)

    # IN  http://192.168.0.8:8000/static/recipe/20190228_163410_monkfish and red pepper skewers.txt
    # url = url.replace(" ", "%20")          # WORKS 
    # OUT http://192.168.0.8:8000/static/recipe/20190228_163410_monkfish%20and%20red%20pepper%20skewers.txt

    url = urllib.parse.quote(url, safe='/:')  # WORKS - likely more robust
    print(url)
    
    local_file_name = f"./scratch/{recipe_text_filename}"    
    print(local_file_name)

    try:
        ret_val = urllib.request.urlretrieve(url, local_file_name)    
        #pprint(ret_val)
    
        file_info  = Path(local_file_name)
        
        if file_info.is_file():
            print(f"File exists: {file_info}")
            f = open(local_file_name, 'r')              # load local file to work with
        else:
            print(f"File NOT PRESENT: {file_info}")
            return
    
        recipe_text = f.read()    
        f.close()
    
    except Exception as e:
        msg = f"Recipe txt file not present: {recipe_text_filename}"
        log_exception(msg, e)
        recipe_text = f"---- for the missing recipe (1)\n100\t ingredients\n  Total (0g)"
        
    finally:
        print(f"RETRIEVED URL: finally segment") 
    
    #recipe_name = re.match(r'\d{8}_\d{6}_(.*?).txt',recipe_text_filename).group(1)
    
    # pull relevant item from a multi component recipe
    for m in re.finditer( r'(^-+- for the.*?Total \(.*?\))', recipe_text, re.MULTILINE | re.DOTALL ):
        recipe_text = m.group(1)
        print(recipe_text)
        
        match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
        if match and (match.group(1) == recipe_name):
            # Matches
            # 1 - name
            # 2 - portions
            # 3 - ingredients
            # 4 - yield
            #match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
            
            # easy to detect failure in the data
            recipe_info = {
                'ri_name':"Initialised as NO MATCH",
                'ingredients':"Pure green",
                'portions': 0,
                'yield': '0g'
            }
        
            if (match):
                recipe_info['ri_name'] = match.group(1).strip()
                recipe_info['portions'] = match.group(2).strip()
                recipe_info['yield'] = match.group(4).strip()
                
                # the return group is split mid line - this is used to fix that
                i_list = (''.join( match.group(3).strip() ) ).split("\n")
                
                # remove comments (after #) from ingredients in recipe: 10g allspice     # woa that's gonna be strong!
                for index, line in enumerate(i_list):
                    i_list[index] = ( re.sub('#.*', '', line) ).strip()
                    
                
                for index, line in enumerate(i_list):                
                    i_list[index] = list( filter(None, line.split("\t")) )
                
                
                print(f"NAME: {match.group(1).strip()}")
                print(f"PORTIONS: ({match.group(2).strip()})")
                print(f"INGREDIENTS:\n")
                pprint(i_list)
                print(f"YIELD: {match.group(4).strip()}")
                
                recipe_info['ingredients'] = i_list
                
            else:
                msg = f"BAD TEMPLATE IN {recipe_text_filename}"
                print(f"{msg} < - = - = - = - = - = - = - = - = - = - = < < !!")        
                # raise exception here
                log_exception(msg, e)
    
    return recipe_info


def create_recipe_info_dictionary(sql_dict, ri_id):
    info = sql_dict[ri_id]
    updated_info = {'ingredients':[]}
    
    # get ingredients from text file while learning templates  . . 
    ingredients_et_al = get_recipe_ingredients_and_yield(info['text_file'],info['ri_name'])
    
    try:
        print(f">------------------------------ MERGED < S")
        
        if (info['ri_name'] == ingredients_et_al['ri_name']):
            print("# merge ingredients into info")
            updated_info = {**info, **ingredients_et_al}
        else:
            print("# titles not the same!! waaa?")
            print(f">{info['ri_name']}< != >{ingredients_et_al['ri_name']}<")
    
                
        for k, v in updated_info.items():
            print(f"> > > K:{k} - V:{v} {type(v)}") # .__class__.__name__}")
    
        for item in updated_info['ingredients']:
            print(f"I> {item[0]} - {item[1]} <")
            
        print(f"\n>------------------------------ MERGED < E")          
        
    except Exception as e:
        log_exception(f"create_recipe_info_dictionary: {ri_id}", e)        
        
    finally:
        print(f"createD recipe_info_dictionary: {ri_id}") 

    
    return updated_info


def inc_recipe_counter(max_id):
    
    file_name = './scratch/rcp_count.txt'
    
    if Path(file_name).is_file():
        f = open(file_name, 'r')
        count = f.read()
        if count == '':
            count = 0 
        f.close()
        print(f"read counter:{count}")        
        count = int(count)
        count += 1
        count = count % (max_id-1)   # loop after reaching max_id
        
    else:
        print(f"initialise counter:0")
        count = 0

    f = open(file_name, 'w')
    f.write(str(count))
    f.close()
    print(f"wrote counter:{count}")

    return count



    
if __name__ == '__main__':
    print("-----  get CSV ------------------------------------S")
    fetch_file = 'http://192.168.0.8:8000/static/sql_recipe_data.csv'
    get_csv_from_server_as_disctionary(fetch_file)
    print("-----  get CSV ------------------------------------E")

    recipe_text = '20190228_163410_monkfish and red pepper skewers.txt'
    #recipe_text = '20190109_143622_crabcakes.txt'
    #urllib.request = 'http://192.168.0.8:8000/static/recipe/20190109_143622_crabcakes.txt'
    get_recipe_ingredients_and_yield(recipe_text,'crabcakes')
