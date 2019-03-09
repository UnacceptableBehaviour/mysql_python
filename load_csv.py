#! /usr/bin/env python

# load a csv file into a list of dictionaries

import csv

from pprint import pprint # giza a look

file_name = './static/sql_recipe_data.csv'

with open(file_name) as csv_to_sql_file:    
    csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')    
    
    pprint(csv_reader)
    
    count = 0
    #pprint(csv_to_sql_file)
    
    list_of_keys = []
    
    for name in csv_reader.fieldnames:
        print(f"N: {name} <")
    
    #for element in array_of_things:
    for row in csv_reader:        
        # print header row
        if count == 0:
            print(f'\n{ len(row) }')
            print(f'Column names: { " | ".join(row) }')            
            pprint(row)
            count += 1
            line = ''
            for col in row:
                line = line + f", {col}"
                list_of_keys.append(col)
            print(line)
            print('- - - - - - - - - - - - - - - - - - - - - - - - LKS')
            pprint(list_of_keys)
            print('- - - - - - - - - - - - - - - - - - - - - - - - LKE')
            print(f'\n')
    
        #rcp_id,image_filename,recipe_title,txt_ingredient_file,n_En,n_Fa,n_Ca,n_Su,n_Pr,n_Sa
        print(f'{row["rcp_id"].ljust(4)}{row["recipe_title"].ljust(50)}{row["n_En"].ljust(4)}')
    
    
    print("\n\nNOW FOR KEYS")
    #csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')
            
    print(f"csv_reader: {csv_reader}")
    pprint(csv_reader) 
    
    print('- - - - - - - - - - - - - - - - - - - - - - - - R2S')
    pprint(list_of_keys)
    print('- - - - - - - - - - - - - - - - - - - - - - - - R2M')

    for col_key in csv_reader.fieldnames:
        print(f"CK: {col_key} <")

    print('- - - - - - - - - - - - - - - - - - - - - - - - R2E')
    
    
    for new_row in csv_reader:
        print(f"ROW: {new_row} <")

        line = ''
        
        for col_key in csv_reader.fieldnames:
            print(f"CK: {col_key} <")
            print(line)
            line = line + " " + new_row[col_key]

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
