#! /usr/bin/env python

# load a csv file into a list of dictionaries

import csv

from pprint import pprint # giza a look

file_name = './static/sql_recipe_data.csv'

with open(file_name) as csv_to_sql_file:    
    csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
    
    count = 0
    #pprint(csv_to_sql_file)
    
    list_of_keys = []
    
    #for element in array_of_things:
    for row in csv_reader:        
        # print header row
        if count == 0:
            print(f'\n{ len(row) }')
            print(f'Column names: { " | ".join(row) }')            
            pprint(row)
            #count += 1
            line = ''
            for col in row:
                line = line + f", {col}"
                list_of_keys.append(col)
            print(line)
            print(f'\n')
    
        #rcp_id,image_filename,recipe_title,txt_ingredient_file,n_En,n_Fa,n_Ca,n_Su,n_Pr,n_Sa
        print(f'{row["rcp_id"].ljust(4)}{row["recipe_title"].ljust(30)}{row["n_En"].ljust(4)}')
    
    



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
