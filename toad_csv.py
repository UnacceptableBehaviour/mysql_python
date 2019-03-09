#! /usr/bin/env python

# load a csv file into a list of dictionaries

import csv
import itertools

from pprint import pprint # giza a look

file_name = './static/sql_recipe_data.csv'

with open(file_name) as csv_to_sql_file:    
    csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
    
    pprint(csv_reader)
    
    for row in csv_reader:
        #print(f"ROW: {row} <")

        line = ''
        
        for col_key in csv_reader.fieldnames:
            #print(f"CK: {col_key} <")
            #print(line)
            line = line + " " + row[col_key]

        print(line)   

    # print image files    
    # doesn't execute - StopIteration
    for row in csv_reader:
        #print(f"ROW: {row} <")

        line = ''
        
        for col_key in csv_reader.fieldnames:
            #print(f"CK: {col_key} <")
            #print(line)
            line = line + " " + row[col_key]

        print(line)   

    


# def main():
# 
#     # for line in db_lines:
#     #     #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
#     #     formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | \n"
#     # 
#     # print(f"\n\nProcess Query {formatted_text}")
#     #     
#     # print(f"\n\nHello World > {engine}" <)
# 
# 
# if __name__ == '__main__':
#     main()
