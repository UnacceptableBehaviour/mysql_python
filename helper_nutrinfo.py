#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
from pprint import pprint 
from config_files import get_file_for_data_set            

class Nutrients:
    match_lookup = {                    # translate from human readable text to dict
        'energy':'n_En',
        'fat':'n_Fa',
        'saturates':'n_Fs',             # 'fat-saturates':'n_Fs',
        'mono-unsaturates':'n_Fm',      # 'fat-mono-unsaturates':'n_Fm',
        'poly-unsaturates':'n_Fp',      # 'fat-poly-unsaturates':'n_Fp',
        'omega_3_oil':'n_Fo3',          # 'fat-omega_3':'n_Fo3',
        'carbohydrates':'n_Ca',
        'sugars':'n_Su',
        'fibre':'n_Fb',
        'starch':'n_St',
        'protein':'n_Pr',
        'salt':'n_Sa',
        'alcohol':'n_Al'    
    }
    
    log_nutridata_key_errors = []
    
    def __init__(self, ingredient='name_of_ingredient', nutridict={}): # nutridict={}):
        self._nutridict = {                  # self.nutridict - instance var
            'name': ingredient,
            'x_ref': None,
            'servings': 0,
            'serving_size': 0.0,
            'yield': '0g',
            'units': 'g',
            'density': 1, 
            'n_En':0.0,   # energy
            'n_Fa':0.0,   # fat
            'n_Fs':0.0,   # fat-saturates
            'n_Fm':0.0,   # fat-mono-unsaturates
            'n_Fp':0.0,   # fat-poly-unsaturates
            'n_Fo3':0.0,  # fat-omega_3
            'n_Ca':0.0,   # carbohydrates
            'n_Su':0.0,   # sugars
            'n_Fb':0.0,   # fibre
            'n_St':0.0,   # starch
            'n_Pr':0.0,   # protein
            'n_Sa':0.0,   # salt
            'n_Al':0.0    # alcohol
        }.update(nutridict)  #(nutridict - passed in)
       

    @property
    def nutridict(self):        
        return self._nutridict
 
    @nutridict.setter                           #
    def nutridict(self, **kwargs):              # https://pythontips.com/2013/08/04/args-and-kwargs-in-python-explained/
        self._nutridict.update(kwargs)

    
    @classmethod
    def process_text_to_nutrients_dict(cls, text_data, nutri_dict):
        if type(nutri_dict).__name__ != 'dict':
            nutri_dict = {}

        # normalise DTK
        normalise = 1.0         # leave non DTK alone

        # scan for nutrients
        nut2ObjLUT = Nutrients.match_lookup                

        # match groups
        # 1 ingredient name
        # 2 servings / source < assumes nutirnt data is per 100g
        # 3 nutrients
        # 4 yield (weight of ingredient providing calories)
        for m in re.finditer(r'^-+ for the nutrition information(.*?)\((.*?)\)$(.*?)Total \((.*?)\)', text_data, re.MULTILINE | re.DOTALL ):
            nutridict_for_pass = {}
            name = m.group(1).strip()
            
            if (name == ''): continue             # skip blank templates
                                    
            nutridict_for_pass['name'] = name
            
            if ('ml' in m.group(4)):
                nutridict_for_pass['yield'] = float(m.group(4).replace('ml', ''))
                nutridict_for_pass['units'] = 'ml'
            else:
                nutridict_for_pass['yield'] = float(m.group(4).replace('g', ''))
            
            if (m.group(2) == 'per 100g'):                      # 100g per serving
                nutridict_for_pass['serving_size'] = 100.0
            elif ('ndb_no=' in m.group(2) ):                    # cross reference in place of per 100g
                nutridict_for_pass['serving_size'] = 100.0
                nutridict_for_pass['x_ref'] = m.group(2)
            elif (m.group(2).replace('per ', '') == m.group(4)):                  # yield and serving same. .
                nutridict_for_pass['serving_size'] = nutridict_for_pass['yield']  # need to normalise nutrients to 100g
                nutridict_for_pass['servings'] = 1.0
                if nutridict_for_pass['serving_size'] == 0:
                    normalise = 1.0
                else:
                    normalise = 100.0 / nutridict_for_pass['serving_size']
            
            #print(f"\n\n** {name} - {m.group(2)} \n {m.group(3)} \n {m.group(4)} \n--")
            
            lines = [ line.strip() for line in m.group(3).split("\n")] # remove leading/training space
            
            lines = list( filter(None, lines) )                 # remove blanks & empty elements
            
            for line in lines:
                #print(f"L:{len(line)} - [{line}]");
                pair = [ item.strip() for item in line.split() ]    # split line by white space, strip excess space off                
                #pprint(pair)
                try:
                    nutridict_for_pass[ nut2ObjLUT[pair[0]] ] = float(pair[1]) * normalise
                except KeyError:
                    Nutrients.log_nutridata_key_errors.append(pair[0])
                except ValueError:
                    if (',' in pair[1]): pair[1] = pair[1].replace(',','.')
                    if (pair[1] == '.'): pair[1] = '0.0'
                    if ('g' in pair[1]): pair[1] = pair[1].replace('g','')
                    nutridict_for_pass[ nut2ObjLUT[pair[0]] ] = float(pair[1]) * normalise
                    
            # TODO 
            # insert = Nutrients(name, nutridict_for_pass)
            # nutri_dict[name] = insert.nutridict
            # print('- - - - - * - - - - - * - - - - - * - - - - - * - - - - - * - - - - - * - - - - - * ')
            # pprint(insert)
            # pprint(insert.nutridict)
            #-
            #nutri_dict[name] = Nutrients(name, nutridict_for_pass).nutridict # issue w/ @property / mutator

            nutri_dict[name] = nutridict_for_pass  # WORKS

        print("SCANNING. . . complete")        
        
        return nutri_dict
        

class NutriDictError(Exception):
    '''TODO Move this and other error classes to separate file: exceptions.py'''
    pass

class AccessError(NutriDictError):
    '''Raised when interface used incorrectly'''
    pass

class DemoMultipleCatch(NutriDictError):
    '''How to catch multiple exception types'''
    pass

class ResourceLocked(NutriDictError):
    '''No other threads yet so should not happen!'''
    pass
    

# Singleton interface for the NutrientsDB
class NutrientsDB:
    #__nutrients_db_file = 'ingredient_db.json'
    __nutrients_db_file = get_file_for_data_set('nutrients_txt_db')
    __nutrients_db = {}
    __seek_misses = []
    __nutrients_loaded = False
    __instance = None
    __file_lock = False # threading.Lock()  # import threading

    @classmethod
    def getInstance(cls):
        '''Return handle to Nutrients Databas - simple file'''
        if NutrientsDB.__instance == None:
            NutrientsDB()
            
        return NutrientsDB.__instance

    @classmethod
    def get(cls, ingredient):
        '''Retrieve nutrients for an ingredient - local version'''
        if ingredient in NutrientsDB.__nutrients_db:
            return NutrientsDB.__nutrients_db[ingredient]
        else:
            NutrientsDB.__seek_misses.append(ingredient)
            return None
    
    @classmethod
    def set(cls, ingredient, nutridict={}):
        '''Shallow write to DB - locally stored'''
        NutrientsDB.__nutrients_db[ingredient] = nutridict


    @classmethod
    def commit(cls):
        '''Write the local version back to DB'''        
        # NutrientsDB.__file_lock.acquire()     # lock resource
        if NutrientsDB.__file_lock == False:
            NutrientsDB.__file_lock = True
            try:
                with open('ingredient_db.json', 'w') as f:
                    f.write(json.dumps(ingredient_db))
                
            except (NotImplementedError, DemoMultipleCatch) as e:
                print("WARNING FAILED to commit DB to disk")
                print(f"\n***\n{e} \n<")

            finally:
                f.close()
                # NutrientsDB.__file_lock.release()
                NutrientsDB.__file_lock = False
        else:
            raise ResourceLocked("Something unexpected going on squire.")
            
        
    # load DB if not loaded
    def __init__(self):
        if NutrientsDB.__instance != None:
            raise AccessError("Access NutrientsDB via getInstance() class method")
            return
        else:
            NutrientsDB.__instance = self

        if NutrientsDB.__nutrients_loaded == False:
            NutrientsDB.loadNutrientsFromTextFile(NutrientsDB.__nutrients_db_file, NutrientsDB.__nutrients_db)
            if (NutrientsDB.__len__() > 0):
                NutrientsDB.__nutrients_loaded = True
                print(f"SUCCESS: Loaded {NutrientsDB.__len__()} ingredients.")
                      
    
    @classmethod                    
    def loadNutrientsFromTextFile(cls, nutri_file, nutri_dict):
        '''Load nutrient information from text file and load it into Dict'''
        try:
            with open(nutri_file, 'r') as f:
                nutrition_items_text = f.read()
                Nutrients.process_text_to_nutrients_dict(nutrition_items_text, nutri_dict)
            
        except (FileNotFoundError, NotImplementedError) as e:
            print("WARNING Exception raised: loadNutrientsFromTextFile")
            print(f"nutri_file: {nutri_file}")
            print("nutri_dict:")
            pprint(nutri_dict)
            print(f"\n***\n{e} \n<")          

    
    @classmethod
    def __len__(cls):
        return len(NutrientsDB.__nutrients_db.keys()) 

    @classmethod
    def list_seek_misses(cls):
        pprint(NutrientsDB.__seek_misses)
        return NutrientsDB.__seek_misses


i_db = NutrientsDB.getInstance()


if __name__ == '__main__':

    ingredient_db = NutrientsDB.getInstance()
    ingredient_db2 = NutrientsDB.getInstance()      # should be the same DB
    #ingredient_db3 = NutrientsDB()                 # Exception: Access NutrientsDB via getInstance class method
    
    print("= = SHOW GLOBAL VARLIST")
    pprint(globals())
    print("<\n\n")
    
    print("= = SHOW protagonists")
    print("--> ingredient_db")
    print(type(ingredient_db))
    print(len(ingredient_db))
    print(id(ingredient_db))
    
    print("\n--> ingredient_db2")
    print(type(ingredient_db2))
    print(len(ingredient_db2))
    print(id(ingredient_db2))
    
    # print("\n--> ingredient_db3")
    # print(type(ingredient_db3))
    # print(len(ingredient_db3))
    # print(id(ingredient_db3))
    # 
    pprint( ingredient_db.get('flour') )
    pprint( ingredient_db.get('coffee') )
    pprint( ingredient_db.get('pork chop') )
    pprint( ingredient_db.get('spinach tortilla') )
    print(f"Seek Misses:\n{NutrientsDB.list_seek_misses()}")
    
    t_dict = {}
    i_db = NutrientsDB.getInstance()
    i_db.loadNutrientsFromTextFile(get_file_for_data_set('dtk_nutrients_txt'), t_dict)
    print("t_dict")
    pprint(t_dict)




# TODO - understand this
# class AttrDict(dict):
#     def __init__(self, *args, **kwargs):
#         super(AttrDict, self).__init__(*args, **kwargs)
#         self.__dict__ = self
# from
# https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
