#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import itertools
from pprint import pprint
from pathlib import Path

from helpers_db import get_ingredients_as_text_list

class FoodSetsError(Exception):
    '''TODO Move this and other error classes to separate file: exceptions.py'''
    pass

class UnkownAllergenType(FoodSetsError):
    '''Raised when interface used incorrectly - non existent allergen type passed in'''
    pass

class IncorrectTypeForIngredients(FoodSetsError):
    '''Ingredients should be str or list'''
    pass

# simple allergen detection - this could explode into a massively time consuming exersize so keep it simple!
# Brief: should work with the ingredients in the current data set ~1400 ingredients
# Basic guide: https://www.food.gov.uk/sites/default/files/media/document/top-allergy-types.pdf
#
# a call to get_allergens_from_ingredients(['cod','flour','egg','water','soda water','salt','veg oil','corn flour'])
# should return ['dairy', 'eggs', 'fish', 'gluten']
#
# 'alcohol classification should be limited to rum', vodka, gin, whisky, red wine, white wine, champagne, cava, scrumpy
# - that's enough for scope of this exersize
#
#
# # # #
# the section following allergens is to deal with classifying for belief systems: IE no beef, no pork,
# veggie, vegan, etc
# Need to classify

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DAIRY
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
dairy_basic = {'milk','cows milk','goats milk','sheeps milk','fermented milk','yogurt','cream','butter','cheese',
               'casein','custard','ice cream','milk powder'}

# usually product of some type katsuobushi or fish sauce for example
dairy_derived_no_recipe =  {'panna cota','brussels pate', 'cheese cake', 'creme patissiere','roulade'}

# different names same thing
dairy_alt = [
    {'yoghurt','yogurt'},
    {'custard', 'creme anglaise'},
    {'creme patissiere', 'creme patissier'},
    {'whippy-san','whippy san'},
    {'parmesan','parmigiano-reggiano'},
    {'mature cheddar','mature cheddar cheese'},
    {'roquefort','roquetfort'},   # 2nd is misspelling
    {'st agur','st agur cheese','saint agur blue cheese'},
    {'feta','feta cheese','greek feta'},
    {'philadelphia','philadelphia soft cheese','cream cheese','soft cheese','soft white cheese'},
    {'brie','somerset brie'},  
]  

# have to give cheese a super set of its own!
# notes on categories here: https://recipes.howstuffworks.com/food-facts/different-types-of-cheese.htm
cheese_subsets = {
    'fresh cheese' : {'cottage cheese','queso fresco','cream cheese','mascarpone','ricotta','ricotta lite','chevre','feta','feta light','cotija','panela','halloumi','fromage blanc','queso blanco'}, # feta can be an aged cheese too
    'cream cheese' : {'philadelphia','roule','garlic roule','garlic & herb roule','boursin'},
    'pasta filata' : {'mozzarella','burrata','provolone','queso oaxaca','scamorza affumicata','caciocavallo','cheddar mozzarella 50/50 mix','chefs larder grated mozzarella and cheddar','chedoza','grated mozzarella and cheddar'},
    'soft-ripened cheese' : {'brie','camembert','cambozola','goats cheese','chavroux goats cheese'},       # bloomy rind
    'semi-soft cheese' : {'havarti','muenster','jarlsberg','chaumes','red leicester'},
    'washed-rind cheese' : {'limburger','taleggio','epoisses','alsatian munster'},
    'blue cheese' : {'roquefort','stilton','gorgonzola','sweet gorgonzola','danish blue', 'st agur'},
    'semi-hard cheese' : {'cheddar','gouda','mature gouda','edam','monterey jack','emmental','swiss','gruyere','extra mature cheddar',
                          'mature cheddar','mild cheddar','leerdammer light cheese','leerdammer'},
    'hard cheese' : {'parmesan','parmigiano-reggiano','asiago','pecorino','manchego',},
    'unsorted' : {'cheese slices','wensleydale cheese','port salut cheese','president brie','edam mild wedge','french camembert',
                  'president camembert','jarlsberg cheese','german cambozola','swiss le gruyere','cinco lanzas 16 months',
                  'taleggio cheese','petit pont leveque cheese','hochland sortett','castello extra creamy brie',
                  'grated mozzarella','austrian smoked cheese','blue stilton standard','saint agur creme',
                  'butlers blacksticks blue','inglewhite farmhouse blue cheese','castello creamy blue ',
                  'abergavenny goats cheese'}
}

cheese = {'cheese'}
for cheese_cat, cheese_set in cheese_subsets.items():
    cheese = cheese | {cheese_cat} | cheese_set

# subsets - common name with various types
dairy_subsets = {
    'milk' : {'skimmed milk','semi skimmed milk','full fat milk','whole milk','1% skimmed milk','1% milk','2% milk','bob'},
    'fermented milk' : {'sour cream','soured milk'},
    'yogurt' : {'greek yoghurt','natural yoghurt','skyr'},
    'cream' : {'single cream','double cream','squirty cream','whipping cream','clotted cream','creme fraiche'},
    'butter' : {'salted butter','cornish butter','ghee','clarified butter'},
    'cheese' : cheese,
    'casein' : {'milk protein','whey protein'},    
    'ice cream' : {'gelato','ice milk','whippy san','frozen custard','frozen yoghurt'},
}



def build_dairy_set():
    dairy = {'dairy'}
    
    for key, val in dairy_subsets.items():
        union = val | {key}     # include the categegory generalisation
        dairy = dairy | union
        
    for val in dairy_alt:
        dairy = dairy | val       # include different names for each dairy
    
    dairy = dairy | dairy_derived_no_recipe
    
    dairy = dairy | dairy_basic
    
    return dairy

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EGGS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
eggs_basic = {'eggs','egg','quails egg','duck egg','hens egg','albumin','albumen','dried egg','powdered egg',
              'egg solids','egg white','egg yolk'}

# usually product of some type katsuobushi or fish sauce for example
eggs_derived_no_recipe =  {'lecithin','marzipan','marshmallows','nougat','pretzels','pasta', 'eggnog','lysozyme'
                           'mayo','mayonnaise','meringue','meringue powder','ovalbumin','surimi','egg tofu'}

def build_eggs_set():
    eggs = {'eggs'}
        
    eggs = eggs | eggs_derived_no_recipe
    
    eggs = eggs | eggs_basic
    
    return eggs


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PEANUTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
peanuts_basic = {'peanuts', 'peanut'}

# usually product of some type katsuobushi or fish sauce for example
peanuts_derived_no_recipe =  {'peanut butter'}

def build_peanuts_set():
    peanuts = {'peanuts'}
        
    peanuts = peanuts | peanuts_derived_no_recipe
    
    peanuts = peanuts | peanuts_basic
    
    return peanuts


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# NUTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
nuts_basic = {'almonds','brazil nuts','cashews','chestnuts','filberts','hazelnuts','hickory nuts','macadamia nuts',
              'pecans','pistachios','walnuts'}

nuts_derived_no_recipe = {'mortadella','salted cashews','honey roast peanuts','honey roast cashews','baklava','cantuccini'}

def build_nuts_set():
    nuts = {'nuts'}
    
    nuts = nuts | nuts_derived_no_recipe
    
    nuts = nuts | nuts_basic
    
    return nuts


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_LUPIN       - related to peanut
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_lupin_basic = {'lupin','lupin seeds','lupin flour'}

#seeds_lupin_derived_no_recipe =  {'',''}

# different names same thing
# seeds_lupin_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]

# subsets - common name with various types
#seeds_lupin_subsets = { }

def build_seeds_lupin_set():
    seeds_lupin = {'seeds_lupin'}
    
    # for key, val in seeds_lupin_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_lupin = seeds_lupin | union
    #     
    # for val in seeds_lupin_alt:
    #     seeds_lupin = seeds_lupin | val       # include different names for each
    # 
    # seeds_lupin = seeds_lupin | seeds_lupin_derived_no_recipe
    
    seeds_lupin = seeds_lupin | seeds_lupin_basic
    
    return seeds_lupin

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_SESAME
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_sesame_basic = {'sesame','sesame seeds','sesame paste','sesame oil','sesame flour','sesame salt'}

# https://allergyfacts.org.au/images/pdf/sesamef.pdf
seeds_sesame_derived_no_recipe =  {'falafel','sesame burger bun', 'sesame bap','gomashio','halva','baklava','pretzels',
                                   'tahina','aqua libra','benne','benniseed','dukkah','gingelly seeds','hummus','pasteli',
                                   'sesarmol','sesomolina','sim sim','til'} # 'tahina' is a sesame sauce!
# different names same thing
seeds_sesame_alt = [
    {'sesame paste','tahini'},
    {'gomasio','gomashio','sesame salt'},
]

# subsets - common name with various types
#seeds_sesame_subsets = {}

def build_seeds_sesame_set():
    seeds_sesame = {'seeds_sesame'}
    
    # for key, val in seeds_sesame_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_sesame = seeds_sesame | union
        
    for val in seeds_sesame_alt:
        seeds_sesame = seeds_sesame | val       # include different names for each seeds_sesame
    
    seeds_sesame = seeds_sesame | seeds_sesame_derived_no_recipe
    
    seeds_sesame = seeds_sesame | seeds_sesame_basic
    
    return seeds_sesame

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_MUSTARD
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_mustard_basic = {'mustard','mustard seeds','french mustard','english mustard','american mustard','yellow mustard',
                       'dijon mustard','dijon','liquid mustard','mustard powder'}

# usually product of some type katsuobushi or fish sauce for example
seeds_mustard_derived_no_recipe =  {'ham sandwich','mayo','mayonnaise','brown mustard','beer mustard','honey mustard','hot mustard','sweet mustard'}

# different names same thing
seeds_mustard_alt = [
    {'whole grain mustard','whole-grain mustard'},
    {'american mustard','yellow mustard'},
]

# subsets - common name with various types
#seeds_mustard_subsets = {}
def build_seeds_mustard_set():
    seeds_mustard = {'seeds_mustard'}
    
    # for key, val in seeds_mustard_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_mustard = seeds_mustard | union
        
    for val in seeds_mustard_alt:
        seeds_mustard = seeds_mustard | val       # include different names for each seeds_mustard
    
    seeds_mustard = seeds_mustard | seeds_mustard_derived_no_recipe
    
    seeds_mustard = seeds_mustard | seeds_mustard_basic
    
    return seeds_mustard

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FISH
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
fish_basic = {'anchovies','barracuda','basa','bass','black cod','blowfish','bluefish','bombay duck','bonito','bream',
              'brill','butter fish','catfish','cod','dogfish','dorade','eel','flounder','grouper','gurnard','haddock',
              'hake','halibut','herring','ilish','john dory','lamprey','ling','lingcod','mackerel','mahi mahi','monkfish',
              'mullet','orange roughy','parrotfish','patagonian toothfish','perch','pike','pilchard','plaice','pollock',
              'pomfret','pompano','sablefish','salmon','sanddab','sardine','sea bass','shad','shark','skate',
              'smelt','snakehead','snapper','sole','sprat','sturgeon','surimi','swordfish','tilapia','tilefish',
              'trout','tuna','turbot','wahoo','whitefish','whiting','witch','whitebait'}

fish_derived_no_recipe = {'katsuobushi','dashi','fish stock cube','fish sauce','cured salmon','smoked salmon','worcestershire sauce'}

# exceptions, sub sets & alternate names
# different name same fish
fish_alt = [
    {'black cod','sablefish'},
    {'patagonian toothfish', 'chilean sea bass'},
    {'dab', 'sanddab'},
    {'witch','righteye flounder'},      # there's about 10 righteye type around australias coast!
    {'sea bass','seabass'},             # the correct spelling is sea bass
    {'summer flounder','fluke'},
    {'river cobler','pangaseus','basa','swai'},
    {'caviar','sturgeon roe'},
    {'ikura','salmon roe'},
    {'kazunoko','herring roe'},
    {'masago','capelin roe'},
    {'tobiko','flying-fish roe'},
    {'anchovies','anchovy'},
    {'worcestershire sauce','lea and perrins'},
    {'ling','cooked ling'},
    {'mackerel','smoked mackerel fillet','mackerel fillet'}
]

# subsets
fish_subsets = {
    'catfish' : {'river cobler','pangaseus','basa','channel catfish','blue catfish','ikan keli','magur','hedu','etta','swai'},
    'cod' : { 'pacific cod', 'atlantic cod' },
    'bass' : {'bass','striped bass'},
    'eel' : {'eel','conger eel'},
    'flounder' : {'plaice','gulf flounder','summer flounder','winer flounder','european flounder','which flounder','halibut','olive flounder'},
    'salmon' : {'sockeye salmon','alaskan salmon','chinook salmon','pink salmon','coho salmon'},    
    'sanddab' : {'pacific sanddab'},   # there are a lot of these
    'shad' : {'alewife','american shad'},
    'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
    'trout' : {'trout','rainbow trout'},    
    'tuna' : {'albacore tuna','bigeye tuna','bluefin tuna','dogtooth tuna','skipjack tuna','yellowfin tuna'},
    'roe' : {'caviar','sturgeon roe','ikura','salmon roe','kazunoko','herring roe','lumpfish roe','masago','capelin roe','shad roe','tobiko','flying-fish roe'}
}


def build_fish_set():
    fish = {'fish'}
    
    for key, val in fish_subsets.items():
        union = val | {key}     # include the categegory generalisation
        fish = fish | union
        
    for val in fish_alt:
        fish = fish | val       # include different names for each fish
    
    fish = fish | fish_derived_no_recipe
    
    fish = fish | fish_basic
    
    return fish


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHELLFISH - MOLLUSCS - theres quite a list here: https://en.wikipedia.org/wiki/List_of_edible_molluscs
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
molluscs_basic = {'abalone','escargot','squid','hereford snail','mussel','limpits','winkles','whelks','clams','mussels',
                  'oyster','scallop','octopus','squid','cuttlefish'}

molluscs_derived_no_recipe =  {'oyster sauce',''}

# different names same thing
molluscs_alt = [
    {'snails','escargot','helix aspersa'},
    {'cuttlefish', 'sepia'},
    {'small squid','small squid tubes','squid tubes','squid'},
]

# subsets - common name with various types
molluscs_subsets = {
    'clams' : { 'blood cockle','cockles','mussels','hard clams','grooved carpet shell','quahog','leukoma','paphies',
               'pismo clam','smooth clam','tuatua' },
    'abalone' : { 'black abalone','blacklip abalone','green abalone','green ormer','haliotis corrugata','red abalone',
                 'white abalone','pāua' },
    'mussels' : { 'blue mussels','blue mussel','california mussel','mediterranean mussel' },
    'oyster' : { 'auckland oyster','dredge oyster','mangrove oyster','ostrea angasi','ostrea edulis','pacific oyster',
                'rock oyster','sydney rock oyster','portuguese oyster'},
    'razor clams' : { 'atlantic jackknife clam','ensis','ensis macha','pacific razor clam','pod razor','razor shell',
                     'sinonovacula' },
}

def build_molluscs_set():
    molluscs = {'molluscs'}
    
    for key, val in molluscs_subsets.items():
        union = val | {key}     # include the categegory generalisation
        molluscs = molluscs | union
        
    for val in molluscs_alt:
        molluscs = molluscs | val       # include different names for each molluscs
    
    molluscs = molluscs | molluscs_derived_no_recipe
    
    molluscs = molluscs | molluscs_basic
    
    return molluscs

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHELLFISH - CRUSTACEANS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
crustaceans_basic = {'crustaceans','langoustine','crab','crayfish','prawns','shrimp','langostino','lobster'}

# usually product of some type katsuobushi or fish sauce for example
crustaceans_derived_no_recipe =  {'salt and pepper squid','lobster bisque', 'shrimp paste'}

# different names same thing
crustaceans_alt = [
    {'langostino', 'squat lobster'},
    {'norway lobster', 'dublin bay prawn', 'langoustine','langostine'},
    {'prawns','shrimp'},
    {'crayfish','crawfish', 'crawdads', 'freshwater lobsters', 'mountain lobsters', 'mudbugs', 'yabbies',
     'cangrejo de rio'},
    {'cangrejo', 'crab', 'crab meat', 'crab claws', 'white crab meat', 'brown crab meat'}
]

# subsets - common name with various types
crustaceans_subsets = {
    'crab' : { 'brown crab','dungeness crab','mud crab','sand crab','alaskan king crab','norwegian king crab','king crab','snow crab','blue crab','soft shell crab' },
    'lobster' : {'american lobster','rock lobster','spiny lobster','red lobster','canadian lobster'},
    'crayfish' : {'marron','koura'},
    'prawns' : {'tiger prawns','king prawns','cooked prawns','fresh prawns','fresh water prawns'}
}
def build_crustaceans_set():
    crustaceans = {'crustaceans'}
    
    for key, val in crustaceans_subsets.items():
        union = val | {key}     # include the categegory generalisation
        crustaceans = crustaceans | union
        
    for val in crustaceans_alt:
        crustaceans = crustaceans | val       # include different names for each
    
    crustaceans = crustaceans | crustaceans_derived_no_recipe
    
    crustaceans = crustaceans | crustaceans_basic
    
    return crustaceans

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ALCOHOL
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
alcohol_basic = {'alcohol','rum','vodka','gin','whisky','red wine','white wine','wine','champagne','cava','scrumpy',
                 'scrumpy jack','larger','cider abv5','corona','corona extra','red wine abv12.5','white wine 12.5',
                 'white wine abv12.5','white wine','tennessee honey lemonade abv5.0','tennessee honey lemonade',
                 'disaronno amaretto liqueur 28%ABV','disaronno amaretto liqueur','disaronno amaretto liqueur abv28',
                 'amaretto liqueur','amaretto','omega cider','port wine','port wine abv18','malbec port','baileys abv17',
                 'baileys','baileys irish cream abv17','mrs irish meadow abv14','mrs irish meadow','sbs madeira abv17.5',
                 'sbs madeira','madeira','marsala','marsala abv18','old rosie'}

# usually product of some type katsuobushi or fish sauce for example
alcohol_derived_no_recipe =  {'rum baba','tiramisu','cocktail'}

# different names same thing
alcohol_alt = [
    {'scrumpy','scrumpy jack'},
    {'larger', 'red stripe'},
    {'cocktails','cocktail'},
]

# subsets - common name with various types
alcohol_subsets = {
    'cocktails' : {'tequila sunrise','black russian','margarita','mojito','caipirina'}
}

def build_alcohol_set():
    alcohol = {'alcohol'}
    
    for key, val in alcohol_subsets.items():
        union = val | {key}     # include the categegory generalisation
        alcohol = alcohol | union
        
    for val in alcohol_alt:
        alcohol = alcohol | val       # include different names for each 
    
    alcohol = alcohol | alcohol_derived_no_recipe
    
    alcohol = alcohol | alcohol_basic
    
    return alcohol

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CELERY
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
celery_basic = {'celery','celery sticks','celery leaves','celery spice','celery seeds','celery salt','celeriac'}

# usually product of some type katsuobushi or fish sauce for example
celery_derived_no_recipe =  {'chicken stock','lamb stock', 'beef stock', 'fish stock', 'pork stock', 'veggie stock',
                             'vegetable stock', 'veg stock', 'chicken stock cube','lamb stock cube', 'beef stock cube',
                             'fish stock cube', 'pork stock cube', 'veggie stock cube', 'vegetable stock cube',
                             'veg stock cube', 'marmite'}

def build_celery_set():
    celery = {'celery'}
        
    celery = celery | celery_derived_no_recipe
    
    celery = celery | celery_basic
    
    return celery



'wheat',
'wheat germ',
'rye',
'barley',
'bulgur',
'couscous',
'farina',
'graham flour',
'kamut',
'khorasan wheat',
'semolina',
'spelt',
'triticale',
'oats',
'oat bran',
'flour'



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GLUTEN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
gluten_basic = {'gluten'}

# usually product of some type katsuobushi or fish sauce for example
gluten_derived_no_recipe =  {'malt vinegar','pasta','bread','pastry','pizza','seitan','flat bread'}

# different names same thing
gluten_alt = [
    {'nan','naan','naaan bread',},
    {'pita','pitta bread'},
    {'rotti','roti'},
]

# subsets - common name with various types
gluten_subsets = {
    'flour' : { 'plain flour','self raising flour','strong flour','bread flour' },
    'flat bread' : {'torta','matzo','pita','naan','roti','paratha','banh','tortilla','wrap','injera','pancake'}, # injera is gluten free if made of 100% teff flour
    'pasta' : {'orzo','spaghetti','macaroni','tagliatele','linguini','fusili','lasagna','rigatoni','farfale','ravioli',
               'fettuccini','penne'}, # a a million other types!
    'bread' : {'sliced bread','sourdough','brown bread','tiger loaf','french stick','giraffe bread','baguette','burger bun',
               'brioche','demi brioche','baton','biscuit','bagel','cornbread','rye bread','milk bread','galic pizza',
               'garlic bread','turkish bread','ciabata','bun','focaccia','mgt','multi grain','seeded batch','thick sliced bread',
               'thick sliced seeded bread','sandwich loaf','white bread','olive bread','poppy seed roll','bap', 'crumpet',
               'seeded baguette','seeded baguette round','baguette round','sourdough round'},
}
def build_gluten_set():
    gluten = {'gluten'}
    
    for key, val in gluten_subsets.items():
        union = val | {key}     # include the categegory generalisation
        gluten = gluten | union
        
    for val in gluten_alt:
        gluten = gluten | val       # include different names for each gluten
    
    gluten = gluten | gluten_derived_no_recipe
    
    gluten = gluten | gluten_basic
    
    return gluten

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SOYA
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
soya_basic = {'soy','soya','edamame','soy sauce','tofu','soy milk','condensed soy milk','miso','soy nuts','tamari','shoyu',
              'teriyaki','tempeh','textured soy protein','tsp','textured vegetable protein','tvp','soy flour',
              'soybean oil','soy lecithin','natto','kinako'}

# usually product of some type katsuobushi or fish sauce for example
soya_derived_no_recipe =  {'condensed soy milk','tofu','douhua'}

# different names same thing
soya_alt = [
    {'soy milk','soymilk'},
    {'soy sauce','tamari','shoyu'},     # tamari is traditionally made soy sauce - does not use wheat and is gluten free
                                        # shoyu is japanese for soy sauce
    {'textured soy protein','tsp'},
    {'textured vegetable protein ','tvp'},
    {'white miso','shiro miso'},
    {'yellow miso','shinshu miso'},
    {'red miso','aka miso'},
    {'teriyaki','teriyaki sauce','teriyake','teriyake sauce'},
    
]

# subsets - common name with various types
soya_subsets = {
    'tofu' : {'silken tofu','extra soft tofu','soft tofu','medium tofu','firm tofu','extra firm tofu','super firm tofu',
              'noodling','tofu noodles','tofu sponge','egg tofu','pressed tofu','fermented tofu','tofu skin','tofu sticks',
              'fried tofu','tofu pockets','tofu puffs'},    
    'miso' : {'red miso','yellow miso','white miso','awase miso','barley miso',}
}

def build_soya_set():
    soya = {'soya'}
    
    for key, val in soya_subsets.items():
        union = val | {key}     # include the categegory generalisation
        soya = soya | union
        
    for val in soya_alt:
        soya = soya | val       # include different names for each soya
    
    soya = soya | soya_derived_no_recipe
    
    soya = soya | soya_basic
    
    return soya

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SULPHUR_DIOXIDE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
sulphur_dioxide_basic = {'sulphur dioxide', 'sulphites'}

# usually product of some type katsuobushi or fish sauce for example
#sulphur_dioxide_derived_no_recipe =  {'',''}

def build_sulphur_dioxide_set():
    sulphur_dioxide = {'sulphur_dioxide'}
        
    #sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_derived_no_recipe
    
    sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_basic
    
    return sulphur_dioxide



#pork
# coppa
# milano salami
# milano salami pre crisp
# milano salami crisp
# modena salami
# modena crisps

conv_list ='''
plain text list here
'''






# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HEADINGS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_allergens_headings():    
    return {'dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'shellfish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'}

# ingredeints for each component already recursed and stored in exploded
# add_subcomponents_ingredients
def does_component_contain_allergen(component, allergen):
    allergen_present = False    
    
    if allergen in get_allergens_headings():    
        allergen_set = allergenLUT[allergen]
    else:
        raise(UnkownAllergenType(f"ERROR: unknown allergen: {allergen} <"))
    
    ingredients_of_component = get_ingredients_as_text_list(component)
    
    if ingredients_of_component == None:     # its an ATOMIC ingredient
        return component in allergen_set
    
    else:
        for i in ingredients_of_component:            
            if i in allergen_set:
                return True

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ALLERGEN SETS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
allergenLUT = {
    'dairy' : build_dairy_set(),
    'eggs' : build_eggs_set(),
    'peanuts' : build_peanuts_set(),
    'nuts' : build_nuts_set(),               
    'seeds_lupin' : build_seeds_lupin_set(),
    'seeds_sesame' : build_seeds_sesame_set(),
    'seeds_mustard' : build_seeds_mustard_set(),
    'fish' : build_fish_set(),
    'molluscs' : build_molluscs_set(),
    'crustaceans' : build_crustaceans_set(),
    'alcohol' : build_alcohol_set(),
    'celery' : build_celery_set(),
    'gluten' : build_gluten_set(),
    'soya' : build_soya_set(),
    'sulphur_dioxide' : build_sulphur_dioxide_set()    
}

def get_allergens_for(list_of_ingredients):
    allergens_detected = []
    
    if list_of_ingredients.__class__ == str:
        list_of_ingredients = [list_of_ingredients]    
    
    if list_of_ingredients.__class__ == list:
        # build complete list - from local DB
        # will not follow URL to inet for ingredients of off the shelf items
        
        add_ingredients = []
        for i in list_of_ingredients:
            add_me = get_ingredients_as_text_list(i)
            if add_me:
                add_ingredients = add_ingredients + add_me
            else:   # ingredient not in DB
                #print(f"INGREDIENT NOT FOUND IN DATABASE: {i} << WARNING * *")
                #print(f"NF:{i}<")
                pass # TODO - log
                    
        
        # flatten so there's only one of each
        list_of_ingredients = list(set(list_of_ingredients + add_ingredients))
        
        for i in list_of_ingredients:
            for allergen in allergenLUT:
                if i in allergenLUT[allergen]:
                    allergens_detected.append(allergen)
    else:
        raise(IncorrectTypeForIngredients("get_allergens_for: pass str or list"))
    
    return allergens_detected


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SETS - CONTAINS FOOD TYPE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def get_tags_from_ingredients_heading(igds):
#     return 'vegan, veggie, cbs, chicken, pork, beef, seafood, crustaceans, gluten_free, ns_pregnant'
#                                                        
# allegen sets
# 'dairy', 'cheese,' 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'shellfish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CHICKEN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
chicken_basic = {'chicken dark meat','chicken breast','chicken','chicken','chicken','chicken','chicken','chicken',
                 'chicken fat','chicken wing w skin','cornfed chicken','chicken wing','chicken roll',
                 'crispy chicken skin','chicken bites','chicken liver','chicken stock cube','chicken stock cubes',
                 'chicken thigh','chicken brown meat','chicken dark meat','chicken breast','poached chicken thigh',
                 'chicken stock','chicken liver','chicken gravy','home made chicken gravy','roast chicken',
                 'fried chicken breast','fried chicken thigh','fried chicken wing','fried chicken quarter',
                 'chicken mince','minced chicken','chicken skin'
                 }

# usually product of some type katsuobushi or fish sauce for example
chicken_derived_no_recipe =  {'mrs chicken korma','chicken korma'}

# different names same thing
chicken_alt = [
    {'chicken dark meat','chicken brown meat','chicken thigh','chicken oysters'},
    #{'another1', 'another2'},
]

# subsets - common name with various types
# chicken_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }

def build_chicken_set():
    chicken = {'chicken'}
    
    # for key, val in chicken_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     chicken = chicken | union
        
    for val in chicken_alt:
        chicken = chicken | val       # include different names for each
    
    chicken = chicken | chicken_derived_no_recipe
    
    chicken = chicken | chicken_basic
    
    return chicken


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PORK
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
pork_basic = {'',''}

#pork
# carvery pork
# pork belly
# roast pork
# trotters
# pigs ears
# roast peppered pork loin
# pork ribs
# pancetta coated pork tenderloin
# pork tenderloin
# pork shoulder
# sweet and sour pork balls in batter
# pork and blue cheese kebab
# pork shoulder stew
# pimped pork shoulder stew
# roast pork w egg on toast and salad
# pork feijoada
# roast pork w feijoada yorkshire pudding
# roast pork mini pitta
# roast pork mini pitta w apple sauce
# roast pork mini pitta and fish fingers
# open roast pork mini pitta w apple sauce
# small pork and egg breakfast
# small pork and egg w red pepper breakfast
# pork stuffing
# stuffed pork and veg stew
# sweetheart cabbage noodles w pork
# pork stew
# pork stew and sweetheart cabbage noodles
# pork shoulder chop
# pork and leek stew
# pork stew w leek and courgette salad

#bacon
# thick smoked bacon
# smoked bacon
# bacon
# bacon lean
# smoked rindless bacon
# bacon frazzles
# bacon and tomato giraffe baguette

# cured
# milano
# salami
# parma
# parma ham
# serano ham
# serano
# lomo
# chorizo
# fuet
# Cumberland sausage
# hot dogs
# breakfast sausages
# charcuterie.

# sausage
# asda chorizo sausages
# cumberland sausage
# bc cumberland sausages
# ttd cumberland sausages
# cumberland sausages
# sausages
# milano cured sausage
# sausage roll dough
# sunchoke mushroom and cured milano sausage broth
# sausage casserole

# pancetta

# ham
# pepper ham
# cooked ham
# ldl smoked ham
# smoked ham
# w&s breadcrumb ham
# parma ham
# sbs parma ham
# sandwich ham
# cooked ham trimmings lidl
# sbs cooked ham
# sbs basics ham
# smoked ham was
# smoked ham trimmings
# ham
# sticky cheese & ham sandwich filling
# mini fish lunch with ham
# ham green beans and cous cous w egg
# king prawn and ham cous cous
# king prawn and ham cous cous amuse bouche
# ham salmon and eggs on tomato toast
# emergency ham and tomato soup small
# tortilla tortilla chips and ham
# leek and ham cous cous
# mini ham and red pepper baguette
# broad bean and potato w/ cured ham salad
# pepper ham and tomato sandwich
# pepper ham and tomato baguette round
# bechamel sauce
# potato salad w ham and grapes
# potato salad and ham snack
# ham frazzles and onion rings
# fruit salad and ham
# fruit ham and nuts
# carbless courgette and ham lasagna
# ham chicken and tomato garlic bread
# fruit and ham breakfast
# ham spinach tortilla
# ham aubergine & courgette in beef broth
# ham apple & lemon basil pizza




# usually product of some type katsuobushi or fish sauce for example
pork_derived_no_recipe =  {'',''}

# different names same thing
pork_alt = [
    {'name1','name2'},
    {'another1', 'another2'},
]

# subsets - common name with various types
pork_subsets = {
    'cod' : { 'pacific cod', 'atlantic cod' },
    'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
}
def build_pork_set():
    pork = {'pork'}
    
    for key, val in pork_subsets.items():
        union = val | {key}     # include the categegory generalisation
        pork = pork | union
        
    for val in pork_alt:
        pork = pork | val       # include different names for each
    
    pork = pork | pork_derived_no_recipe
    
    pork = pork | pork_basic
    
    return pork

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# BEEF
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
beef_basic = {'',''}

# beef
# shortribs
# roast beef
# beef monster munch
# beef pie
# bisto best beef gravy
# beef tomato
# beef tomatoes
# 20% minced beef
# beef silverside w&s
# sbs ttd beef steak burger
# beef burger
# beef stock cube
# mrs beef stock cube as prepared
# beef stock
# mrs beef stock cube
# 12% beef mince
# 15% beef mince
# 20% beef mince
# beef brisket
# beef jerky
# beef fillet
# beef & jalapeno burger
# fast beef gravy
# fast garlic beef chicken gravy
# mushroom risotto broth w beef
# beef and mushroom broth w marmalade and asauce
# beef and mushroom broth w marmalade and asauce
# sliced beef and beefy mushroom broth w spring onion
# beef stock and bean broth
# lamb and beef stock and bean broth w spring onion
# simple beef and onion broth
# beef brisket and lettuce broth
# beef brisket and lettuce broth
# beef and sunchoke and salami broth
# beef kofte
# beef broth & greens
# beef and chicken chunk on beetroot brioche
# beef and chicken burger w cranberry apple on ciabatta
# beef and mushroom broth 2
# beef pie dinner
# beef brisket dinner
# beef broth onions rings and naan bread
# beefy mushroom gravy
# beef and mushroom pie w stuffed tomato
# ham aubergine & courgette in beef broth
# beef on mini brioche
# beef on mini brioche w veg pate
# beef & been sprouts w mushroom broth

# usually product of some type katsuobushi or fish sauce for example
beef_derived_no_recipe =  {'',''}

# different names same thing
beef_alt = [
    {'name1','name2'},
    {'another1', 'another2'},
]

# subsets - common name with various types
beef_subsets = {
    'cod' : { 'pacific cod', 'atlantic cod' },
    'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
}
def build_beef_set():
    beef = {'beef'}
    
    for key, val in beef_subsets.items():
        union = val | {key}     # include the categegory generalisation
        beef = beef | union
        
    for val in beef_alt:
        beef = beef | val       # include different names for each beef
    
    beef = beef | beef_derived_no_recipe
    
    beef = beef | beef_basic
    
    return beef

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # NS_PREGNANT
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
# 
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
# 
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
# 
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#     
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#         
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#     
#     allergen = allergen | allergen_derived_no_recipe
#     
#     allergen = allergen | allergen_basic
#     
#     return allergen

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # DUCK & GAME
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# duck_n_game

# duck
# duck fat
# aunt bessies duck fat roast potatoes
# duck breast meat only raw
# duck meat only raw
# duck leg quarter
# duck thigh
# duck breast
# duck and baked potato w red cabbage

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # COMBINATIONS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#'vegan, veggie, cbs, , , , ns_pregnant'

# not striclty true but from a vegan perspective ok
#seafood = fish | molluscs | crustaceans

# vegan = not animal
#animal = pork | beef | chicken | seafood | dairy | eggs | {'frogs'}

# veggie = not (animal - dairy - eggs)
















# ELEMENTS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # HEADING
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
# 
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
# 
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
# 
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#     
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#         
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#     
#     allergen = allergen | allergen_derived_no_recipe
#     
#     allergen = allergen | allergen_basic
#     
#     return allergen



def main():
    pass

if __name__ == '__main__':
    
    # fish = ''
    # for m in re.finditer(r'^(.*?)$', conv_list, re.MULTILINE | re.DOTALL):
    #     fish += f"'{m.group(1).lower()}',"         
    #     print(f"'{m.group(1).lower()}'")
    #     
    # print(fish)
    # sys.exit()

    # fish_basic, fish_alt (list of sets), fish_subsets (dict of sets)
    # fish = {'fish'}
    # print(len(fish), fish)
    # 
    # for key, val in fish_subsets.items():
    #     print(key, val)
    #     union = val | {key}     # include the categegory generalisation
    #     fish = fish | union
    #     print(union)
    #     print()
    #     
    # print(len(fish), fish)    
    # 
    # for val in fish_alt:
    #     print(val)
    #     fish = fish | val       # include different names for each fish
    #     print()
    #     
    # print(len(fish), fish)
    # 
    # fish = fish | fish_basic
    # 
    # print(len(fish), fish)
    
    #print(build_fish_set())
    
    #print(cheese_subsets)
    
    cheese = {'cheese'}
    #[cheese | cheese_set for cheese_set in cheese_subsets ]
    for cheese_cat, cheese_set in cheese_subsets.items():
        cheese = cheese | {cheese_cat} | cheese_set
    
    print(cheese) # all the cheese
    
    nutrients = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')
    content = ''
    with nutrients.open('r') as f:
        #content = f.readlines()
        content = f.read()

    for m in re.finditer( r'--- for the nutrition information(.*?)\(', content, re.MULTILINE | re.DOTALL ):
        ingredient = m.group(1)
        if re.search("duck", ingredient):
            print(ingredient.strip())
            
    # for line in content:
    #     print(line)
    #     match = re.match(r'--- for the nutrition information(.*?)\(', line, re.MULTILINE | re.DOTALL)
    #     pprint(match)
    #     if match:
    #         print(match.group(1))
    
    
# ELEMENTS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # HEADING
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
# 
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
# 
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
# 
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#     
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#         
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#     
#     allergen = allergen | allergen_derived_no_recipe
#     
#     allergen = allergen | allergen_basic
#     
#     return allergen