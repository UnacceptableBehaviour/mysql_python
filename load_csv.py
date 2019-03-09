#! /usr/bin/env python

# load a csv file into a list of dictionaries

import csv
import itertools

from pprint import pprint # giza a look



def main():

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
    
                line = line + " " + row[col_key]
    
            print(line)
            
            entries +=1
            
    
        entries -= 1
        
        print("----- image_dictionary")
        pprint(image_dictionary)
    
        print("----- text_dicionary")
        pprint(text_dicionary)



    # for line in db_lines:
    #     #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
    #     formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | \n"
    # 
    # print(f"\n\nProcess Query {formatted_text}")
    #     
    # print(f"\n\nHello World > {engine}" <)


if __name__ == '__main__':
    main()
