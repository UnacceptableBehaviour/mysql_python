#! /usr/bin/env python

# load a csv file into a list of dictionaries

print("----- load_csv.py ------------------------------------------------------------ S")
print(f"{__name__}")

import csv
import itertools

from pprint import pprint # giza a look


# serve files from http://192.168.0.8:8000/static/sql_recipe_data.csv
# $ cd /a_syllabus/lang/python/repos/assest_server 
# $ http-server -p 8000 --cors 
import urllib.request
# urllib.request.urlretrieve ("http://192.168.0.8:8000/static/sql_recipe_data.csv", "sql_recipe_data.csv")

print("----- load_csv.py ------------------------------------------------------------ imports done")

def get_csv_from_server_as_disctionary(url):    
    print("----- get_csv ------------------------------------------------------------")
    
    csv_file = url.split('/')[-1]
    
    print(csv_file)
    
    local_file_name = f"./static/{csv_file}"

    urllib.request.urlretrieve (url, local_file_name)

    sql_dict = {}

    with open(local_file_name) as csv_to_sql_file:    
        csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
        
        pprint(csv_reader)
        
        #local_store = './static/'
        image_dictionary = {}
        text_dicionary = {}
        entry = {}
    
        entries = 0
        
        for row in csv_reader:
            line = ''                
            entry = {}                          # create a new dictionary for each entry
            
            for col_key in csv_reader.fieldnames:
                
                entry[col_key] = row[col_key]   # create and info dictionary
                
                if col_key == 'image_filename':
                    image_dictionary[entries] = row[col_key]
                    continue
    
                if col_key == 'txt_ingredient_file':
                    text_dicionary[entries] = row[col_key]
                    continue
    
                line = line + f" {col_key}:" + row[col_key]
    
            #print(f"\n> > {entries}")
            #print(line)                        
            sql_dict[entries] = entry
            #print(f"\n> > {entries}")
            #print(sql_dict[entries])                        
            
            entries +=1

    pprint(sql_dict[0])
    
    print("----- reponse ------------------------------------------------------------")
    
    return sql_dict
    

def main():

    # print("----- reponse ------------------------------------------------------------")
    # response = urllib.request.urlopen("http://192.168.0.8:8000/static/sql_recipe_data.csv")
    # pprint(response)    
    # print("----- content ------------------------------------------------------------")
    # content = response.read()
    # pprint(content)        
    # print("----- rest ------------------------------------------------------------")

    url_file = "http://192.168.0.8:8000/static/sql_recipe_data.csv"

    urllib.request.urlretrieve (url_file, "./static/sql_recipe_data.csv")

    file_name = './static/sql_recipe_data.csv'

    with open(file_name) as csv_to_sql_file:    
        csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
        
        pprint(csv_reader)
        
        local_store = './static/'
        image_dictionary = {}
        text_dicionary = {}
    
        entries = 0
        
        for row in csv_reader:
            line = ''
                        
            for col_key in csv_reader.fieldnames:
    
                if col_key == 'image_filename':
                    image_dictionary[entries] = row[col_key]
                    continue
    
                if col_key == 'txt_ingredient_file':
                    text_dicionary[entries] = row[col_key]
                    continue
    
                line = line + f" {col_key}:" + row[col_key]
    
            print(line)
            
            entries +=1
            
    
        entries -= 1
        
        print("----- image_dictionary")
        pprint(image_dictionary)
    
        print("----- text_dicionary")
        pprint(text_dicionary)

        sql_dict = get_csv_from_server_as_disctionary(url_file)

        print(sql_dict.__class__.__name__)


    # for line in db_lines:
    #     #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
    #     formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | \n"
    # 
    # print(f"\n\nProcess Query {formatted_text}")
    #     
    # print(f"\n\nHello World > {engine}" <)

print("----- load_csv.py ------------------------------------------------------------ checking if main")

print(f"{__name__}")

if __name__ == '__main__':
    main()

print("----- load_csv.py ------------------------------------------------------------ LOADED")