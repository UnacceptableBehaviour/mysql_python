#! /usr/bin/env python

import re
#import sys
#import itertools
from pprint import pprint, pformat
#from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# for expected conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from food_sets import process_OTS_i_string_into_allergens_and_base_ingredients

class ProductInfo:
    CATEGORY_WIDTH = 24
    VALUE_WIDTH = 10
    ENERGY_TO_KCAL = 4.184
    sbs_driver = None  # sbs        # TODO - register driver into a hash: driver['sbs']
    mrs_driver = None  # mrs             # can we use API for this?
    tsc_driver = None  # tsc
    wtr_driver = None  # wtr
    cop_driver = None  # cop
    asd_driver = None  # asd
    ocd_driver = None  # ocd
    bkr_driver = None  # bkr        
    sbs_cookie_barrier = True
    mrs_cookie_barrier = True
    tsc_cookie_barrier = True
    wtr_cookie_barrier = True
    cop_cookie_barrier = True
    asd_cookie_barrier = False
    ocd_cookie_barrier = True
    bkr_cookie_barrier = True
    nutrition_symbol_to_regex    = {
        'energy':            r'energy', #r'(\d+)\s*kj',    # $1 = kcal integer - kJ downcase kj
        'fat':               r'fat',
        'saturates':         r'\bsaturate[sd]\b',
        'mono-unsaturates':  r'mono',
        'poly-unsaturates':  r'poly',
        'omega_3_oil':       r'omega',
        'carbohydrates':     r'carbohydrate',
        'sugars':            r'sugar',
        'starch':            r'starch',
        'protein':           r'protein',
        'fibre':             r'fibre',
        'salt':              r'salt',
        'alcohol':           r'alcohol'
    }
    
    def initialise_nutrient_hash(self):
        return { k: 0.0 for k,v in ProductInfo.nutrition_symbol_to_regex.items() }

                    
    def __init__(self, name, url, igdt_type):
        self.ri_name            = name  # nick_name
        self.igdt_type          = igdt_type
        self.product_name       = ''
        self.price_per_package  = 0
        self.units              = '?'               # g, kg, l, ml, ea (each)     [all lower case]
        self.qty                = 0
        self.no_of_each         = 0                 # 6 for pack of 6 apples, units = 'ea', multipack_qty = 1
        self.package_in_g       = 0
        self.alt_package_in_g   = 0                 # package weight from title in g
        self.package_qty_str    = ''                # package weight from title
        self.price_per_measure  = 0                 # price per measurement unit 3.80 / kg
        self.multipack_qty      = 1                 # 4 tins of 415g - this number is 4, 6x1L milk it would be 6,
                                                    # 6 pack of apples this would be 1 and the units would be 'ea'
        self.supplier_item_code = ''
        self.product_url        = url
        self.supplier_name      = ''
        self.nutrition_info     = self.initialise_nutrient_hash() 
        self.i_list             = []    # ingredient list
        self.i_text             = ''    # ingredient raw text as scraped
        self.allergens          = set() # pulled from ingredient list
        self.allergens_raw      = ''    # scraped allergens section
        self.product_desc       = ''
        self.product_page       = None   
        
        self.get_product_info()        
        self.i_text = self.remove_ingredients_title(self.i_text)
        self.nutrinfo_text = self.build_nutri_string()
        

    def __str__(self):
        json = pformat(vars(self), indent=2, sort_dicts=False)
        #return str(pprint(vars(self)))
        #print(json)
        return json


    def remove_ingredients_title(self, i_string):
        m = re.search(r'(ingredients:)',i_string,re.I)
        if m:
            i_string = i_string.replace(m.group(1),'')
        return i_string


    def build_nutri_string(self):
        # build nutrient        
        nutrient_string = f"------------------ for the nutrition information {self.ri_name} ({self.product_url})\n"
        
        for nut, val in self.nutrition_info.items():
            if nut == 'energy':
                nutrient_string = nutrient_string + f"{nut}".ljust(20)+"\t"+f"{ round(val, 0) }".rjust(10)+"\n"
            else:
                nutrient_string = nutrient_string +  f"{nut}".ljust(20)+"\t"+f"{ round(val, 2) }".rjust(10)+"\n"
        
        nutrient_string = nutrient_string +  "Total (100g)".rjust(60)+"\n"
        
        nutrient_string_to_file = f"\n\n{nutrient_string}ingredients: {self.i_text}\nigdt_type: {self.igdt_type}"
            
        return (nutrient_string_to_file)


    def nutrinfo_str(self):
        # template = ''
        # for nut, qty in self.nutrition_info:
        return self.nutrinfo_text

    def display_all_tags(self, driver):
        print("#>> DA tags - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - S")
        try:
            #css_selector = 'h1[data-test-id="pd-product-title"]'
            css_selector = '*'
            e_list = driver.find_elements(By.CSS_SELECTOR, css_selector)
            for e in e_list:
                #object_methods = [method_name for method_name in dir(object) if callable(getattr(object, method_name))]
                #print('methods')
                #print([method_name for method_name in dir(e) if callable(getattr(e, method_name))])
                #print('m--')
                print(f"\n>TAG: <{e.tag_name}>")
                print(f"class: {e.get_attribute('class')} <")
                print(f"data-test-id: {e.get_attribute('data-test-id')} <")
                print(f"Text: {e.text} <")
                #print(f"Text: {e.text} <")
                pprint(e)
                # print(f"{}")
            
        except Exception as exp:
            print('Expetion S')
            print(exp.msg)
            print('Expetion E')        
        print("#>> DA tags - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - E")
        
    def convert_pkg_str_to_qty_in_g(self):          #     ea                kg                g
        # (Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|L|l) - (Loose|Pack|Each) - (Litre|Kg|L|l) - (mg|Ml|ml|g|G|Grams)  
        qty_in_g = 0
        multiplier = 1

        if (self.units == 'kg') or (self.units == 'l') or (self.units == 'litre') or (self.units == 'litres'):
            multiplier = 1000
            
        qty_in_g = self.qty * multiplier

        if (self.units == 'loose') or (self.units == 'pack') or (self.units == 'each') or (self.units == 'ea'):
            qty_in_g = None
            self.units == 'ea'
            self.no_of_each = self.qty

        self.alt_package_in_g = qty_in_g    
        self.package_in_g = qty_in_g        # this is overwritten with more accurate data if available




    def scrape_sainsburys(self):        
        print(f"scraping SAINSBURIES: {self.product_url}")        
            # find which column the per 100g/ml is 

        # - - - - Helpers factor out where generic - - - S
        def get_nutr_per_100g_col(table_header, default_col=1):
            col_100 = None
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S)
            for col,text in enumerate(head_cols):
                col_100 = col
                if re.search(r'100[gml]+', text): return(col_100)

            return(default_col)
        
        # replace 2,2 w/ 2.2
        # replace (2,2) w/ 2.2
        # convert mg & ug into g
        def remove_g_and_less_than(str_g: str) -> float:
            str_g = str_g.lower()
            multiplier = 1

            # TODO switch code so it uses ug as standard unit
            if 'mg' in str_g:
                str_g = str_g.replace('mg', '')
                multiplier = 1.0 / 1000.0

            if ('mcg' in str_g) or ('μg' in str_g) or ('ug' in str_g):
                str_g = str_g.replace('mcg', '').replace('μg', '').replace('ug', '')
                multiplier = 1.0 / 1000000.0                
            
            str_g = str_g.replace('g', '').replace('(', '').replace(')', '').replace(',', '.').replace('trace', '0.01')

            if '&lt;' in str_g or '<' in str_g:        
                str_g = str_g.replace('&lt;', '').replace('<', '')
            
                return round(float(str_g) * multiplier * 0.8, 2)
            
            return round(float(str_g) * multiplier, 2) 
        # - - - - Helpers factor out where generic - - - E
        
        # register driver
        if ProductInfo.sbs_driver == None:
            ProductInfo.sbs_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.sbs_driver

        # remove cookie request            
        cookie_btn_timeout_inSec = 3
        driver.get(self.product_url)

        # TODO - H use Tesco cookie - wait click together
        allow_cookies_btn_id = 'onetrust-accept-btn-handler'
        if ProductInfo.sbs_cookie_barrier:
            try:
                print('try cookie_button w WAIT')
                cookie_button = WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.presence_of_element_located((By.ID, allow_cookies_btn_id)))
                print('cookie_button')
            except TimeoutException:
                print("Loading took too much time!")
            except Exception as exp:
                print(exp.msg)
                print('cookie_button NOT FOUND')
            
            try:
                print('cookie_button CLICK')
                cookie_button.send_keys(Keys.RETURN)
                ProductInfo.sbs_cookie_barrier = False            
            except Exception as exp:
                print(exp.msg)
                print('cookie_button NOT clicked')

        # wait content load
        delay_in_seconds = 2  # TODO is this an actual delay = bad, or a timeout = fine if so rename - check API
        try:    
            css_selector = 'h3.productDataItemHeader, h3.itemHeader'
            print(f'# # #> waiting for h3 tags: {css_selector}')
            h3_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            print(f'# # #> found for h3 tags:\n{h3_tags}')
        except TimeoutException:
            print("Waiting for INGREDIENTS took too much time!")
        except Exception as exp:
            print(exp.msg)
            print('Ingredients NOT FOUND')
        
        # self.product_name             Sainsbury's British Semi Skimmed Milk
        # self.package_qty_str          (1.13L) 2 pint
        # self.alt_package_in_g         1130 grams
        #
        # <h1 class="pd__header" data-test-id="pd-product-title">Sainsbury's Pearl Barley 500g</h1>
        # >TAG: <h1>
        # class: pd__header <
        # data-test-id: pd-product-title <
        # Text: Sainsbury's Pearl Barley 500g <
        #
        # \b(x*\d+[.mlLgKk]*)\b
        # Chavroux La Buche Goats Cheese (150g)                 match in brackets
        # Sainsbury's White Granulated Sugar (5kg)
        # Blue Dragon Original Thai Sweet Chilli Sauce (190ml)
        # Blue Dragon Original Thai Sweet Chilli Sauce (380g)
        # Yeo Valley Organic Free Range Semi Skimmed Milk (1L)
        # Sainsbury's British Semi Skimmed Milk (1.13L) 2 pint
        # Sainsbury's British Semi Skimmed Milk (2.27L) 4 pint
        # Sainsbury's Fairtrade Bananas (x5)
        try:
            # css_selector = 'h1[class=pd__header][data-test-id=pd-product-title]' # SAME - works
            css_selector = 'h1.pd__header[data-test-id=pd-product-title]' 
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.product_name = e.text.strip()
            # in case there is no size specified get size from product name
            m = re.search(r'\b(x*\d+[.mlLgKk]*)\b', self.product_name)
            if m: self.package_qty_str = m.group(1)
            
        except Exception as exp:
            print(exp.msg)
            print('self.product_name NOT found!')         
        
        # self.price_per_package            £5.50 £2.21/kg  - can appear together
        #                                     ^^
        # <div aria-label="£1.80 was £2.40">£1.80</div
        # <div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined"><div aria-hidden="true"><span data-test-id="offer-original-price" class="pd__cost__original" aria-label="original price">£2.40</span></div><div aria-label="£1.80 was £2.40">£1.80</div></div>
        # <div aria-label="65p was undefined">65p</div>
        # <div data-test-id="pd-retail-price" class="pd__cost__total undefined"><div aria-label="65p was undefined">65p</div></div>
        #                       ^
        try:
            css_selector = 'div[data-test-id="pd-retail-price"]'
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.price_per_package = e.text.strip().replace('now\n','')   # TODO replace anything left of 'now\n' as in was $4.40 now £3
            self.package_in_g = 99999999
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_package NOT found!')


        # collect product info          description, package size, ingredients, manufacturer, packaging, etc
        # list of PAIRS of h3.productDataItemHeader and div.productText 

        # >>> list = driver.find_elements(By.CSS_SELECTOR,'h3.productDataItemHeader, div.productText')
        # >>> pprint(list)
        # [<selenium.webdriver.remote.webelement.WebElement (session="97f3784a97842e5220dfe009d47e96d0", element="227f94ae-f2ef-4547-a3fe-15004956af84")>,
        #  <selenium.webdriver.remote.webelement.WebElement (session="97f3784a97842e5220dfe009d47e96d0", element="2394d653-8540-46de-896e-3873afb77ff4")>,
        # .
        # .
        # <selenium.webdriver.remote.webelement.WebElement (session="97f3784a97842e5220dfe009d47e96d0", element="e1574eb0-b607-4a3e-90e5-4e3b7acc38df")>]
        # >>> list[0].text
        # 'Description'
        # >>> list[1].text
        # 'Cured pork salami seasoned with pepper & garlic.\n  Lightly seasoned with pepper & garlic. \nA traditional Italian salami, produced in the heart of Italy with Italian pork.  \n  Great as part of an Italian inspired charcuterie platter or why not try using as an ingredient on a Pizza to provide a delicate and meaty taste.'
        # >>> list[2].text
        # 'Nutrition'
        # >>> list[3].text
        # 'Per 4 slices Typical Values\nENERGY\n342kJ\n82kcal\n4%\nFAT\n6.6g\n9%\nSATURATES\n2.5g\n13%\nSUGARS\n<0.5g\n<1%%\nSALT\n0.82g\n14%\n% of the Reference Intakes\nTypical Values Per 100g : Energy 1591 kJ/383 kcal\nRI= Reference intake of an average adult (8400 kJ/2000 kcal)\nTable of Nutritional Information\nTypical Values Per 100g  Per 4 slices  % based on RI for Average Adult\nEnergy 1591kJ 342kJ -\n383kcal 82kcal 4%\nFat 30.7g 6.6g 9%\nSaturates 11.5g 2.5g 13%\nMono-unsaturates 14.7g 3.2g -\nPolyunsaturates 3.1g 0.7g -\nCarbohydrate 1.0g <0.5g -\nSugars <0.5g <0.5g -\nFibre <0.5g <0.5g -\nProtein 25.7g 5.5g 11%\nSalt 3.81g 0.82g 14%\nReference intake of an average adult (8400 kJ / 2000 kcal)\nThis pack contains 4 servings'
        # >>> list[4].text
        # 'Ingredients'
        # >>> list[5].text
        # 'INGREDIENTS:Pork, Salt, Sugar, Dextrose, White Pepper, Antioxidant: Sodium Ascorbate; Garlic, Preservatives: Potassium Nitrate, Sodium Nitrite.\nPackaged in a protective atmosphere'
        # >>> list[6].text
        # 'Country of Origin'
        # >>> list[7].text
        # "Packed in Italy, Italy for Sainsbury's Supermarkets Ltd, London EC1N 2HT using pork from Italy."
        # >>> list[8].text
        # 'Size'
        # >>> list[9].text
        # '86g'
        # >>> list[10].text
        # 'Storage'
        # >>> list[11].text
        # 'For use by date: see front of pack. Keep Refrigerated. Once opened, use within 2 days and do not exceed the use by date. Open pack 15 minutes before serving to allow the flavours to develop'
        # >>> list[12].text
        # 'Packaging'
        # >>> list[13].text
        # "Don't Recycle base Film\nDon't Recycle top Film\nRecycle base Label"
        # >>> list[14].text
        # 'Manufacturer'
        # >>> list[15].text
        # "We are happy to replace this item if it is not satisfactory\nSainsbury's Supermarkets Ltd.\n33 Holborn, London EC1N 2HT\nCustomer services 0800 636262"        

        item_info = {}
        try:            
            e_list = driver.find_elements(By.CSS_SELECTOR,'h3.productDataItemHeader, div.productText')  
            elements = iter(e_list)
            for elem in elements:
                ne = next(elements)
                # sometime ingredient all in one element
                el_text = elem.text #.lower()
                if re.match(r'ingredient[s]?\b',el_text,re.I):
                    i_list = re.sub(r'ingredient[s]?\b','',el_text,flags=re.I)
                    print(f'ingredient - MATCH [{len(i_list)}]\n{el_text}\ni_list>{i_list}<E')
                    if len(i_list.strip()) > 0:                        
                        self.i_text = i_list.strip()
                    else:
                        item_info[elem.text.lower()] = ne
                else:
                    item_info[elem.text.lower()] = ne
                print(f"\nt:>{elem.text.lower()}<\nne:{ne}\nc:>{ne.text}<\n\n")
            
        except Exception as exp:
            print(exp.msg)
            print('ERROR processing item_info PAIRS - NOT found!')

        print('+>> item_info')
        pprint(item_info)
            
        if 'size' in item_info:     # not always present
            self.package_in_g = item_info['size'].text      # TODO H - process text SB wiegit in grams
        else:
            self.package_in_g = self.alt_package_in_g
        
        print('ingredients  - - - - S')
        print(f"('ingredients' in item_info): {('ingredients' in item_info)}")
        print(f"(self.i_text == ''): {(self.i_text == '')}")
        print('ingredients  - - - - E')
        if ('ingredients' in item_info) and (self.i_text == ''):
            self.i_text       = item_info['ingredients'].text
        
        if self.i_text == '':
            print('- - -: * * * INGREDIENTS NOT FOUND')            

        if self.igdt_type == 'atomic':
            print(f"- - -: * * * {self.ri_name} - ATOMIC . . . .  self.i_text = '__igdts__'")
            self.i_text = '__igdts__'
        
        if 'description' in item_info:
            self.product_desc = item_info['description'].text



        print('- - - - - - - nutrition - - - - - - - S')
        # <table class="nutritionTable">
        #     <thead>
        #         <tr class="tableTitleRow">
        #         <th scope="col">Typical Values
        #         (cooked as per instructions)</th><th scope="col">Per 100g&nbsp;</th><th scope="col">Per 80g serving&nbsp;</th><th scope="col">% based on RI for Average Adult</th>
        #         </tr>
        #     </thead>
        #     <tbody>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader" rowspan="2">Energy</th><td class="tableRow1">477kJ</td><td class="tableRow1">381kJ</td><td class="tableRow1">-</td>
        #         </tr>
        #         <tr class="tableRow0">
        #             <td class="tableRow0">113kcal</td><td class="">90kcal</td><td class="">5%</td>
        #         </tr>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader">Fat</th><td class="tableRow1">&lt;0.5g</td><td class="nutritionLevel1">&lt;0.5g</td><td class="nutritionLevel1">1%</td>
        #         </tr>
        #     </tbody>
        # </table>
        
        # item_info['nutrition']
        nut_regex = ProductInfo.nutrition_symbol_to_regex
        row_data = []
        col_100 = 1

        # nutrition tabe
        try:
            tb_rows = driver.find_elements(By.CSS_SELECTOR, 'table.nutritionTable tr')
            rows = iter(tb_rows)
            tb_head = next(rows)    # first row always col titles
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S) # TODO REMOVE
            
            col_100 = get_nutr_per_100g_col(tb_head)
            
            print(f"--H: {head_cols}")
            for row in rows:
                cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',row.get_attribute('innerHTML'))
                print(f"-R: {cols}")
                row_data.append(cols)
                for n_type, n_regex in nut_regex.items():
                    if re.search(n_regex, cols[0].lower()):
                        #self.nutrition_info[n_type] = cols[col_100]
                        if n_type == 'energy':
                            # in single row:  2143 kJ /<br> 513 kcal or on two rows!
                            e_str = cols[col_100].lower().replace('/', '')
                            
                            m = re.search(r'(\d+)\s*kcal', e_str)
                            if m:
                                kcal = m.group(1)                                
                                self.nutrition_info[n_type] = int(kcal)
                            else:
                                print(f"\tenergy: NO MATCH:{e_str}")
                                if 'kj' in e_str:                                    
                                    kj_to_kcal = e_str.replace('kj','').strip()
                                    kj_to_kcal = int(float(kj_to_kcal) * 0.239006)
                                    self.nutrition_info[n_type] = int(kj_to_kcal)
                        else:
                            self.nutrition_info[n_type] = remove_g_and_less_than(cols[col_100])
            
            pprint(self.nutrition_info)
            
        except StopIteration as exp:
            print(exp)
            print('ERROR processing nutrition table - NOT found!')
        
        print('- - - - - - - nutrition - - - - - - - E')

        
        
        # self.price_per_measure  = 0.0
        # <div data-test-id="pd-unit-price" class="pd__cost__per-unit" aria-label="unit price and measure on offer">£12.00 / kg</div>
        # <div data-test-id="pd-unit-price" class="pd__cost__per-unit" aria-label="unit price and measure on offer">£2.11 / 100g</div>
        #                       ^
        try:
            css_selector = '[data-test-id="pd-unit-price"]'
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.price_per_measure = e.text.strip().replace('(','').replace(')','')
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_measure NOT found!')
            
        # self.supplier_item_code = ''
        # <p class="pd__item-code">Item code: <span id="productSKU">952811</span></p>        
        try:
            e = driver.find_element(By.CSS_SELECTOR, '#productSKU')
            self.supplier_item_code = e.text.strip()
        except Exception as exp:
            print(exp.msg)
            print('self.supplier_item_code NOT found!')                    
            
        self.supplier_name      = 'Sainburys'



        

    def scrape_morrisons(self):
        # TODO - check for product no longer exits
        #        can be NO LONGER STOCKED
        #            or OOPS  - tomato splat - URL out of date / incorrect
        print(f"scraping MORRISONS: {self.product_url}")        

        # - - - - Helpers factor out where generic - - - S
        # TODO factor out
        def get_nutr_per_100g_col(table_header, default_col=1):
            col_100 = None
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S)
            for col,text in enumerate(head_cols):
                col_100 = col
                if re.search(r'100[gml]+', text): return(col_100)

            return(default_col)
        
        # replace 2,2 w/ 2.2
        # replace (2,2) w/ 2.2
        # convert mg & ug into g
        def remove_g_and_less_than(str_g: str) -> float:
            str_g = str_g.lower()
            multiplier = 1

            # TODO switch code so it uses ug as standard unit
            if 'mg' in str_g:
                str_g = str_g.replace('mg', '')
                multiplier = 1.0 / 1000.0

            if ('mcg' in str_g) or ('μg' in str_g) or ('ug' in str_g):
                str_g = str_g.replace('mcg', '').replace('μg', '').replace('ug', '')
                multiplier = 1.0 / 1000000.0                
            
            str_g = str_g.replace('g', '').replace('(', '').replace(')', '').replace(',', '.').replace('trace', '0.01')

            if '&lt;' in str_g or '<' in str_g:        
                str_g = str_g.replace('&lt;', '').replace('<', '')
            
                return round(float(str_g) * multiplier * 0.8, 2)
            
            return round(float(str_g) * multiplier, 2) 
        # - - - - Helpers factor out where generic - - - E
        
        # register driver
        if ProductInfo.mrs_driver == None:
            ProductInfo.mrs_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.mrs_driver

        DSK = 0
        MOB = 1
        BY  = 0
        SEL = 1
        cur = DSK
        query = {
            'cookie_b':             [(By.CSS_SELECTOR, '#onetrust-accept-btn-handler'),
                                     (By.CSS_SELECTOR, '#onetrust-accept-btn-handler')],
            'product_title':        [(By.CSS_SELECTOR, 'header > h1'), 
                                     (By.CSS_SELECTOR, 'header > h1')],
            # 'package_qty_str':      [(By.CSS_SELECTOR,'.bop-catchWeight'),
            #                          (By.CSS_SELECTOR,'.bop-catchWeight')],                                     
            'price_per_package':    [(By.CSS_SELECTOR, '.bop-price__current'),
                                     (By.CSS_SELECTOR, '.bop-price__current')],
            'price_per_measure':    [(By.CSS_SELECTOR, '.bop-price__per'),
                                     (By.CSS_SELECTOR, '.bop-price__per')],
            'item_info':            [(By.CSS_SELECTOR, 'h6, .bop-info__content'),                                     
                                     (By.CSS_SELECTOR, '.gn-expandableBar__header, .bop-info__content')], # Gets Description but misses i_string / allergies
            'nutri_table':          [(By.CSS_SELECTOR, '.bop-nutritionData__origin > table tr'),
                                     (By.CSS_SELECTOR, '.bop-nutritionData__origin > table tr')],            
            
            # '':[(,),(,)],
        }
        item_info = {
            'description': [],
            'ingredients': [],
            'dietary information': [],
            #'allergy information': [],  
            #'number of uses': [],
            #'net contents': []
        }

        # for desktop replace [DSK] for [MOB] for mobile
        # (query['cookie_b'][DSK][BY], query['cookie_b'][DSK][SEL])
        # or
        # query['cookie_b'][cur] where cur = DSK or MOB
        # WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][DSK])).click()

        # remove cookie request
        cookie_btn_timeout_inSec = 5  
        driver.get(self.product_url)

        if ProductInfo.mrs_cookie_barrier:
            try:
                print(f'try cookie_button w WAIT: {cookie_btn_timeout_inSec}')
                WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][cur])).click()
                print('CLICKED cookie_button')
                ProductInfo.mrs_cookie_barrier = False
            except TimeoutException:
                print("Loading took too much time!")

        # wait content load
        # TODO H - get info at same time as wait load
        # selector
        h_tags = h2_tags = ''
        delay_in_seconds = 1
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:
            print(f'# # #> waiting for Title & QTY CSS:')
            h_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
            h_tags = h_tags.text.strip()
            print(f'# # #> found h_tags:\n{h_tags}')
        except TimeoutException:
            print("# # # TIMEOUT> Waiting for Title took too much time!")
            cur = MOB if cur == DSK else MOB
        except Exception as exp:
            print(exp.msg)
            print('Title NOT FOUND')
            cur = MOB if cur == DSK else MOB
        
        if not h_tags:        
            print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
            try:            
                print(f'# # #> waiting for Title & QTY XPATH:')
                h2_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
                h2_tags = h2_tags.text.strip()
                print(f'# # #> found h2_tags:\n{h2_tags}')
            except TimeoutException:
                print(f'# # # TIMEOUT> waiting for Title & QTY XPATH:')
            except Exception as exp:
                print(exp.msg)
                print('Title NOT FOUND - h2_tags')

        
        # self.product_name             British Semi Skimmed Milk
        # self.package_qty_str          (1.13L) 2 pint
        # self.alt_package_in_g         1130 grams
        #      
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:

            if h_tags or h2_tags:                
                self.product_name = h_tags if h_tags else h2_tags 
                self.product_name = self.product_name.strip()
                print(f"[self.product_name] {self.product_name} < h_tags {h_tags}<  h2_tags {h2_tags}<")
            else:
                try:
                    print(f"[self.product_name] {self.product_name} < * * * NO h_tags or h2_tags * * *")
                    e = driver.find_element(*query['product_title'][cur])
                    self.product_name = e.text.strip()                
                except Exception as exp:
                    print(exp.msg)
                    print('self.product_name NOT found! no h / h2 / or retry')

            # remove multipack X no
            multibuy_rgx = r'(\d+)\s*x'
            m = re.search(multibuy_rgx, self.product_name, re.I)
            if m:
                product_name_multiby_removed = self.product_name.replace(m.group(0), '')
                self.multipack_qty = m.group(1)
            else:
                product_name_multiby_removed = self.product_name

            # in case there is no size specified get size from product name            
            alt_package_in_g_rgx = r'(([\.\d]+)\s*(Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|L|l)\s*(?:(\/)?\d+\s*Pint(?:s)?)?)'
            m = re.search(alt_package_in_g_rgx, product_name_multiby_removed, re.I)
            if m:
                self.package_qty_str = m.group(1)
                self.units = m.group(3)
                self.qty = round(float(m.group(2).strip()),2)
                self.convert_pkg_str_to_qty_in_g() # alt_package_in_g <- None if units is Pack / Loose
                print(f"INFO FROM TITLE  - - - - - - - - : S [self.package_qty_str] - {self.package_qty_str} <")
                print(f"self.product_name: {self.product_name}<")
                print(f"self.package_qty_str: {self.package_qty_str}<")
                print(f"self.package_in_g: {self.package_in_g}<")
                print(f"self.alt_package_in_g: {self.alt_package_in_g}<")
                print(f"self.units: {self.units}<")
                print(f"self.qty: {self.qty}<")
                print(f"self.no_of_each: {self.no_of_each}<")
                print("INFO FROM TITLE  - - - - - - - - : E")
            
        except Exception as exp:
            print(exp.msg)
            print('self.product_name NOT found!')         
        
        # self.price_per_package            £5.50 £2.21/kg  - can appear together
        #                                     ^^
        # <div aria-label="£1.80 was £2.40">£1.80</div
        # <div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined"><div aria-hidden="true"><span data-test-id="offer-original-price" class="pd__cost__original" aria-label="original price">£2.40</span></div><div aria-label="£1.80 was £2.40">£1.80</div></div>
        # <div aria-label="65p was undefined">65p</div>
        # <div data-test-id="pd-retail-price" class="pd__cost__total undefined"><div aria-label="65p was undefined">65p</div></div>
        #                       ^
        # self.price_per_package    in      price-per-sellable-unit
        # self.price_per_measure    in      price-per-quantity-weight        
        print(f"\n\nquery['price_per_package'][{cur}] {query['price_per_package'][cur]}")
        try:
            #css_selector = '.price-per-sellable-unit'
            e = driver.find_element(*query['price_per_package'][cur])
            self.price_per_package = e.text.strip().replace('now\n','')
            self.package_in_g = 99999999
            print(f"£/pkg: {self.price_per_package} [self.price_per_package]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_package NOT found!')

        
        print(f"\n\nquery['price_per_measure'][{cur}] {query['price_per_measure'][cur]}")
        try:
            #css_selector = '.price-per-quantity-weight'
            e = driver.find_element(*query['price_per_measure'][cur])
            self.price_per_measure = e.text.strip().replace('(','').replace(')','')
            print(f"£/unit: {self.price_per_measure} [self.price_per_measure]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_measure NOT found!')

        # Product Description (TODO) & Infomation
        # document.querySelectorAll('h2.product-info-block__title')
        # gives description and 
        # 
        # all rest under Information
        #
        # more generic gives all info blocks except nutrition (whic we already have)
        # document.querySelectorAll('div.product-info-block')

        # >>> list = driver.find_elements(By.CSS_SELECTOR,'div.product-info-block, .product-info-block__content')

        print(f"\n\nquery['item_info'][{cur}] {query['item_info'][cur]}")

        e_list = []
        try:            
            e_list = driver.find_elements(*query['item_info'][cur]) 
        except Exception as exp:
            print(exp.msg)
            #pprint(exp)
            print('ERROR processing item_info PAIRS - NOT found!')

        item_info_markers = list(item_info.keys())

        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - S')
        # skip on fin=d
        i = 0
        while i < len(e_list):
            elmnt = e_list[i]
            found_mk = None
            for marker in item_info_markers:
                print(f"\n{i:02} - {elmnt.text.lower()} - Mkr: {marker}")
                if i+1 < len(e_list): print(f"{i+1:02} - {e_list[i+1]}\n{e_list[i+1].text}")
                if marker == elmnt.text.lower().strip():
                    item_info[marker].append(e_list[i+1].text)
                    print(f"STORE:{i:02}[{marker}] {elmnt.text} <")
                    print(f"item_info[{marker}]:{item_info[marker]} <") 
                    found_mk = marker
                    i += 1  # skip next index
                    break
            if found_mk: item_info_markers.remove(found_mk)
            i += 1
        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - E')


        print('+>> item_info - - - - - - - - - - - - - - - - - - - S')
        pprint(item_info)
        print('+>> item_info - - - - - - - - - - - - - - - - - - - E')
                
        # Pack size in Product Description - TODO L 
        # Net Contents also has same info ? multibuy
        if 'size' in item_info:     # not always present
            self.package_in_g = item_info['size'][0]
        else:
            self.package_in_g = self.alt_package_in_g
        
        print('ingredients  - - - - - - - - S')
        print(f"len(item_info['ingredients']) {len(item_info['ingredients'])}")
        print(f"item_info['ingredients'] {item_info['ingredients']} <")
                                                # TODO scan for water salt oil and only other ingredients - cashews, smoke mackerel
        if len(item_info['ingredients']) == 0:  # if no ingredient assume atomic roqufort, milk, smoked mackerel
            print(f"NO INGREDIENT FOUND: {item_info['ingredients']} <")
            self.i_text = ''
            self.igdt_type = 'atomic'            
        else:
            self.i_text = item_info['ingredients'][0]
            ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.i_text, self.ri_name)
            self.allergens = ots_info['allergens']
            print(f"- - - - - - - ots_info")
            pprint(ots_info)
            self.i_list = ots_info['i_list']
            if len(self.i_list) == 1: 
                print(f"ATOMIC: len(self.i_list) [{len(self.i_list)}]\n{self.i_list}\nself.i_text: {self.i_text}")
                self.igdt_type = 'atomic'
            else:
                self.igdt_type = 'ots'  # override ctor atomic
        
        # product may have been set atomic by args passed to constructor/init
        if self.igdt_type == 'atomic':
            print(f"- - -: * * * {self.ri_name} - ATOMIC . . . .  self.i_text = '__igdts__'\n self.i_text was: {self.i_text} <")
            self.i_text = '__igdts__'


        # update allergens from scrape info - tsc
        #if (len(item_info['allergy information']) > 0): self.allergens_raw = item_info['allergy information'][0] # tsc       
        if (len(item_info['dietary information']) > 0): self.allergens_raw = item_info['dietary information'][0] # mrs

        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.allergens_raw, self.ri_name)
        
        print(f"processing self.allergens_raw[{self.allergens_raw}] = [{ots_info['allergens']}]")
        
        self.allergens.update(ots_info['allergens'])
        if (self.igdt_type == 'atomic') and (len(self.allergens)) and (self.i_text == '__igdts__'):
            self.i_text = f"{self.ri_name}, (contains {', '.join(self.allergens)})"

        print('ingredients  - - - - - - - - E')        
        
        if 'product description' in item_info:      
            # TODO need to process/accumulate down to 'Information' and pull out Pack size if present
            self.product_desc = item_info['product description']



        print('- - - - - - - nutrition - - - - - - - S')
        # <table class="nutritionTable">
        #     <thead>
        #         <tr class="tableTitleRow">
        #         <th scope="col">Typical Values
        #         (cooked as per instructions)</th><th scope="col">Per 100g&nbsp;</th><th scope="col">Per 80g serving&nbsp;</th><th scope="col">% based on RI for Average Adult</th>
        #         </tr>
        #     </thead>
        #     <tbody>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader" rowspan="2">Energy</th><td class="tableRow1">477kJ</td><td class="tableRow1">381kJ</td><td class="tableRow1">-</td>
        #         </tr>
        #         <tr class="tableRow0">
        #             <td class="tableRow0">113kcal</td><td class="">90kcal</td><td class="">5%</td>
        #         </tr>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader">Fat</th><td class="tableRow1">&lt;0.5g</td><td class="nutritionLevel1">&lt;0.5g</td><td class="nutritionLevel1">1%</td>
        #         </tr>
        #     </tbody>
        # </table>
        
        # item_info['nutrition']
        nut_regex = ProductInfo.nutrition_symbol_to_regex
        row_data = []
        col_100 = 1

        # nutrition table - - - - WORKING: on both layouts
        try:
            tb_rows = driver.find_elements(*query['nutri_table'][cur])
            rows = iter(tb_rows)
            tb_head = next(rows)    # first row always col titles
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S) # TODO REMOVE
            
            col_100 = get_nutr_per_100g_col(tb_head)
            
            print(f"--H: {head_cols}")
            for row in rows:
                cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',row.get_attribute('innerHTML'))
                print(f"-R: {cols}")
                row_data.append(cols)
                for n_type, n_regex in nut_regex.items():
                    if re.search(n_regex, cols[0].lower()):
                        #self.nutrition_info[n_type] = cols[col_100]
                        if n_type == 'energy':
                            # in single row:  2143 kJ /<br> 513 kcal or on two rows!
                            e_str = cols[col_100].lower().replace('/', '')
                            
                            m = re.search(r'(\d+)\s*kcal', e_str)
                            if m:
                                kcal = m.group(1)                                
                                self.nutrition_info[n_type] = int(kcal)
                            else:
                                print(f"\tenergy: NO MATCH:{e_str}")
                                if 'kj' in e_str:                                    
                                    kj_to_kcal = e_str.replace('kj','').strip()
                                    kj_to_kcal = int(float(kj_to_kcal) * 0.239006)
                                    self.nutrition_info[n_type] = int(kj_to_kcal)
                        else:
                            self.nutrition_info[n_type] = remove_g_and_less_than(cols[col_100])
            
            pprint(self.nutrition_info)
            
        except StopIteration as exp:
            print(exp)
            print('ERROR processing nutrition table - NOT found!')
        
        print('- - - - - - - nutrition - - - - - - - E')

        # sbs            
        # self.supplier_item_code = ''
        # <p class="pd__item-code">Item code: <span id="productSKU">952811</span></p>        
        # try:
        #     e = driver.find_element(*query['supplier_item_code'][cur])
        #     self.supplier_item_code = e.text.strip()
        # except Exception as exp:
        #     print(exp.msg)
        #     print('self.supplier_item_code NOT found!')                    
            
        self.supplier_name      = 'Morrisons'






    def scrape_tesco(self):
        print(f"scraping TESCO: {self.product_url}")

        # - - - - Helpers factor out where generic - - - S
        # TODO factor out
        def get_nutr_per_100g_col(table_header, default_col=1):
            col_100 = None
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S)
            for col,text in enumerate(head_cols):
                col_100 = col
                if re.search(r'100[gml]+', text): return(col_100)

            return(default_col)
        
        # replace 2,2 w/ 2.2
        # replace (2,2) w/ 2.2
        # convert mg & ug into g
        def remove_g_and_less_than(str_g: str) -> float:
            str_g = str_g.lower()
            multiplier = 1

            # TODO switch code so it uses ug as standard unit
            if 'mg' in str_g:
                str_g = str_g.replace('mg', '')
                multiplier = 1.0 / 1000.0

            if ('mcg' in str_g) or ('μg' in str_g) or ('ug' in str_g):
                str_g = str_g.replace('mcg', '').replace('μg', '').replace('ug', '')
                multiplier = 1.0 / 1000000.0                
            
            str_g = str_g.replace('g', '').replace('(', '').replace(')', '').replace(',', '.').replace('trace', '0.01')

            if '&lt;' in str_g or '<' in str_g:        
                str_g = str_g.replace('&lt;', '').replace('<', '')
            
                return round(float(str_g) * multiplier * 0.8, 2)
            
            return round(float(str_g) * multiplier, 2) 
        # - - - - Helpers factor out where generic - - - E
        
        # register driver
        if ProductInfo.tsc_driver == None:
            ProductInfo.tsc_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.tsc_driver

        DSK = 0
        MOB = 1
        BY  = 0
        SEL = 1
        cur = DSK
        query = {
            'cookie_b':             [(By.CSS_SELECTOR, '.beans-cookies-notification__button'),
                                     (By.CSS_SELECTOR, '.beans-cookies-notification__button')],
            'product_title':        [(By.CSS_SELECTOR, 'h1.product-details-tile__title'),
                                     (By.CSS_SELECTOR, 'h1.styled__ProductTitle-mfe-pdp__sc-ebmhjv-6')],
            'price_per_package':    [(By.CSS_SELECTOR, '.price-per-sellable-unit'),
                                     (By.CSS_SELECTOR, '.styled__Text-qgg5i6-1')],
            'price_per_measure':    [(By.CSS_SELECTOR, '.price-per-quantity-weight'),
                                     (By.CSS_SELECTOR, '.styled__Subtext-qgg5i6-2')],
            'item_info':            [(By.CSS_SELECTOR, '.product-info-block__title, .product-info-block__content'),
                                     (By.CSS_SELECTOR, 'h3.component__StyledHeading-cy778r-0, .styled__Content-mfe-pdp__sc-1od89q4-2')],
            'nutri_table':          [(By.CSS_SELECTOR, 'table.product__info-table tr'),
                                     (By.CSS_SELECTOR, 'table.product__info-table tr')],
            
            # '':[(,),(,)],
            # '':[(,),(,)],
        }
        item_info = {
            'product description': [],
            'ingredients': [],
            'allergy information': [],
            'number of uses': [],
            'net contents': []
        }

        # for desktop replace [DSK] for [MOB] for mobile
        # (query['cookie_b'][DSK][BY], query['cookie_b'][DSK][SEL])
        # or
        # query['cookie_b'][cur] where cur = DSK or MOB
        # WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][DSK])).click()

        # remove cookie request
        cookie_btn_timeout_inSec = 5  
        driver.get(self.product_url)

        if ProductInfo.tsc_cookie_barrier:
            try:
                print(f'try cookie_button w WAIT: {cookie_btn_timeout_inSec}')
                WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][cur])).click()
                print('CLICKED cookie_button')
                ProductInfo.tsc_cookie_barrier = False
            except TimeoutException:
                print("Loading took too much time!")

        # wait content load
        # TODO H - get info at same time as wait load
        # selector
        # asparagus-root > div > div.template-wrapper > main > div > div > div.styled__PDPTileContainer-mfe-pdp__sc-ebmhjv-0.cEAseF.pdp-tile > div > section.styled__GridSection-mfe-pdp__sc-ebmhjv-1.bjEIyj > h1
        
        # chrome class
        # <h1 class="product-details-tile__title">Tesco Black Turtle Beans 500G</h1>

        # slenium chrome class - surfshark
        # <h1 class="product-details-tile__title">Tesco Black Turtle Beans 500G</h1>

        # slenium chrome class
        # <h1 class="component__StyledHeading-cy778r-0 ernAnS styled__ProductTitle-mfe-pdp__sc-ebmhjv-6 flNJKr">Tesco Black Turtle Beans 500G</h1>

        # xpath - startwith: styled__ProductTitle-mfe-pdp  skip uuid tag __sc-ebmhjv-6
        # "//*[starts-with(@class, 'styled__ProductTitle-mfe-pdp')]"
        h_tags = h2_tags = ''
        delay_in_seconds = 1
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:
            print(f'# # #> waiting for Title & QTY CSS:')
            h_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
            h_tags = h_tags.text.strip()
            print(f'# # #> found h_tags:\n{h_tags}')
        except TimeoutException:
            print("# # # TIMEOUT> Waiting for Title took too much time!")
            cur = MOB if cur == DSK else MOB
        except Exception as exp:
            print(exp.msg)
            print('Title NOT FOUND')
            cur = MOB if cur == DSK else MOB
        
        if not h_tags:
            print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
            try:            
                print(f'# # #> waiting for Title & QTY XPATH:')
                h2_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
                h2_tags = h2_tags.text.strip()
                print(f'# # #> found h2_tags:\n{h2_tags}')
            except TimeoutException:
                print(f'# # # TIMEOUT> waiting for Title & QTY XPATH:')
            except Exception as exp:
                print(exp.msg)
                print('Title NOT FOUND - h2_tags')

        
        # self.product_name             British Semi Skimmed Milk
        # self.package_qty_str          (1.13L) 2 pint
        # self.alt_package_in_g         1130 grams
        #      
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:

            if h_tags or h2_tags:                
                self.product_name = h_tags if h_tags else h2_tags 
                self.product_name = self.product_name.strip()
                print(f"[self.product_name] {self.product_name} < h_tags {h_tags}<  h2_tags {h2_tags}<")
            else:
                try:
                    print(f"[self.product_name] {self.product_name} < * * * NO h_tags or h2_tags * * *")
                    e = driver.find_element(*query['product_title'][cur])
                    self.product_name = e.text.strip()                
                except Exception as exp:
                    print(exp.msg)
                    print('self.product_name NOT found! no h / h2 / or retry')

            # remove multipack X no
            multibuy_rgx = r'(\d+)\s*x'
            m = re.search(multibuy_rgx, self.product_name, re.I)
            if m:
                product_name_multiby_removed = self.product_name.replace(m.group(0), '')
                self.multipack_qty = m.group(1)
            else:
                product_name_multiby_removed = self.product_name

            # in case there is no size specified get size from product name            
            alt_package_in_g_rgx = r'(([\.\d]+)\s*(Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|L|l)\s*(?:(\/)?\d+\s*Pint(?:s)?)?)'
            m = re.search(alt_package_in_g_rgx, product_name_multiby_removed, re.I)
            if m:
                self.package_qty_str = m.group(1)
                self.units = m.group(3)
                self.qty = round(float(m.group(2).strip()),2)
                self.convert_pkg_str_to_qty_in_g() # alt_package_in_g <- None if units is Pack / Loose
                print(f"INFO FROM TITLE  - - - - - - - - : S [self.package_qty_str] - {self.package_qty_str} <")
                print(f"self.product_name: {self.product_name}<")
                print(f"self.package_qty_str: {self.package_qty_str}<")
                print(f"self.package_in_g: {self.package_in_g}<")
                print(f"self.alt_package_in_g: {self.alt_package_in_g}<")
                print(f"self.units: {self.units}<")
                print(f"self.qty: {self.qty}<")
                print(f"self.no_of_each: {self.no_of_each}<")
                print("INFO FROM TITLE  - - - - - - - - : E")
            
        except Exception as exp:
            print(exp.msg)
            print('self.product_name NOT found!')         
        
        # self.price_per_package            £5.50 £2.21/kg  - can appear together
        #                                     ^^
        # <div aria-label="£1.80 was £2.40">£1.80</div
        # <div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined"><div aria-hidden="true"><span data-test-id="offer-original-price" class="pd__cost__original" aria-label="original price">£2.40</span></div><div aria-label="£1.80 was £2.40">£1.80</div></div>
        # <div aria-label="65p was undefined">65p</div>
        # <div data-test-id="pd-retail-price" class="pd__cost__total undefined"><div aria-label="65p was undefined">65p</div></div>
        #                       ^
        # self.price_per_package    in      price-per-sellable-unit
        # self.price_per_measure    in      price-per-quantity-weight        
        print(f"\n\nquery['price_per_package'][{cur}] {query['price_per_package'][cur]}")
        try:
            #css_selector = '.price-per-sellable-unit'
            e = driver.find_element(*query['price_per_package'][cur])
            self.price_per_package = e.text.strip().replace('now\n','')
            self.package_in_g = 99999999
            print(f"£/pkg: {self.price_per_package} [self.price_per_package]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_package NOT found!')

        
        print(f"\n\nquery['price_per_measure'][{cur}] {query['price_per_measure'][cur]}")
        try:
            #css_selector = '.price-per-quantity-weight'
            e = driver.find_element(*query['price_per_measure'][cur])
            self.price_per_measure = e.text.strip().replace('(','').replace(')','')
            print(f"£/unit: {self.price_per_measure} [self.price_per_measure]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_measure NOT found!')

        # Product Description (TODO) & Infomation
        # document.querySelectorAll('h2.product-info-block__title')
        # gives description and 
        # 
        # all rest under Information
        #
        # more generic gives all info blocks except nutrition (whic we already have)
        # document.querySelectorAll('div.product-info-block')

        # >>> list = driver.find_elements(By.CSS_SELECTOR,'div.product-info-block, .product-info-block__content')

        print(f"\n\nquery['item_info'][{cur}] {query['item_info'][cur]}")

        e_list = []
        try:            
            e_list = driver.find_elements(*query['item_info'][cur]) 
        except Exception as exp:
            print(exp.msg)
            #pprint(exp)
            print('ERROR processing item_info PAIRS - NOT found!')

        item_info_markers = list(item_info.keys())

        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - S')
        # skip on fin=d
        i = 0
        while i < len(e_list):
            elmnt = e_list[i]
            found_mk = None
            for marker in item_info_markers:
                print(f"\n{i:02} - {elmnt.text}")
                if i+1 < len(e_list): print(f"{i+1:02} - {e_list[i+1]}\n{e_list[i+1].text}")
                if marker == elmnt.text.lower().strip():
                    item_info[marker].append(e_list[i+1].text)
                    found_mk = marker
                    i += 1  # skip next index
                    break
            if found_mk: item_info_markers.remove(found_mk)
            i += 1
        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - E')


        print('+>> item_info - - - - - - - - - - - - - - - - - - - S')
        pprint(item_info)
        print('+>> item_info - - - - - - - - - - - - - - - - - - - E')
                
        # Pack size in Product Description - TODO L 
        # Net Contents also has same info ? multibuy
        if 'size' in item_info:     # not always present
            self.package_in_g = item_info['size'][0]
        else:
            self.package_in_g = self.alt_package_in_g
        
        print('ingredients  - - - - - - - - S')
        print(f"len(item_info['ingredients']) {len(item_info['ingredients'])}")
        print(f"item_info['ingredients'] {item_info['ingredients']} <")
                                                # TODO scan for water salt oil and only other ingredients - cashews, smoke mackerel
        if len(item_info['ingredients']) == 0:  # if no ingredient assume atomic roqufort, milk, smoked mackerel
            print(f"NO INGREDIENT FOUND: {item_info['ingredients']} <")
            self.i_text = ''
            self.igdt_type = 'atomic'            
        else:
            self.i_text = item_info['ingredients'][0]
            ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.i_text, self.ri_name)
            self.allergens = ots_info['allergens']
            print(f"- - - - - - - ots_info")
            pprint(ots_info)
            self.i_list = ots_info['i_list']
            if len(self.i_list) == 1: 
                print(f"ATOMIC: len(self.i_list) [{len(self.i_list)}]\n{self.i_list}\nself.i_text: {self.i_text}")
                self.igdt_type = 'atomic'
            else:
                self.igdt_type = 'ots'  # override ctor atomic
        
        # product may have been set atomic by args passed to constructor/init
        if self.igdt_type == 'atomic':
            print(f"- - -: * * * {self.ri_name} - ATOMIC . . . .  self.i_text = '__igdts__'\n self.i_text was: {self.i_text} <")
            self.i_text = '__igdts__'


        # update allergens from scrape info
        if (len(item_info['allergy information']) > 0): self.allergens_raw = item_info['allergy information'][0]

        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.allergens_raw, self.ri_name)
        
        print(f"processing self.allergens_raw[{self.allergens_raw}] = [{ots_info['allergens']}]")
        
        self.allergens.update(ots_info['allergens'])
        if (self.igdt_type == 'atomic') and (len(self.allergens)) and (self.i_text == '__igdts__'):
            self.i_text = f"{self.ri_name}, (contains {', '.join(self.allergens)})"

        print('ingredients  - - - - - - - - E')        
        
        if 'product description' in item_info:      
            # TODO need to process/accumulate down to 'Information' and pull out Pack size if present
            self.product_desc = item_info['product description']



        print('- - - - - - - nutrition - - - - - - - S')
        # <table class="nutritionTable">
        #     <thead>
        #         <tr class="tableTitleRow">
        #         <th scope="col">Typical Values
        #         (cooked as per instructions)</th><th scope="col">Per 100g&nbsp;</th><th scope="col">Per 80g serving&nbsp;</th><th scope="col">% based on RI for Average Adult</th>
        #         </tr>
        #     </thead>
        #     <tbody>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader" rowspan="2">Energy</th><td class="tableRow1">477kJ</td><td class="tableRow1">381kJ</td><td class="tableRow1">-</td>
        #         </tr>
        #         <tr class="tableRow0">
        #             <td class="tableRow0">113kcal</td><td class="">90kcal</td><td class="">5%</td>
        #         </tr>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader">Fat</th><td class="tableRow1">&lt;0.5g</td><td class="nutritionLevel1">&lt;0.5g</td><td class="nutritionLevel1">1%</td>
        #         </tr>
        #     </tbody>
        # </table>
        
        # item_info['nutrition']
        nut_regex = ProductInfo.nutrition_symbol_to_regex
        row_data = []
        col_100 = 1

        # nutrition table - - - - WORKING: on both layouts
        try:
            tb_rows = driver.find_elements(*query['nutri_table'][cur])
            rows = iter(tb_rows)
            tb_head = next(rows)    # first row always col titles
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S) # TODO REMOVE
            
            col_100 = get_nutr_per_100g_col(tb_head)
            
            print(f"--H: {head_cols}")
            for row in rows:
                cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',row.get_attribute('innerHTML'))
                print(f"-R: {cols}")
                row_data.append(cols)   # TODO is this even used? WHERE? REMOVE - 4 occurences
                for n_type, n_regex in nut_regex.items():
                    if re.search(n_regex, cols[0].lower()):
                        #self.nutrition_info[n_type] = cols[col_100]
                        if n_type == 'energy':
                            # in single row:  2143 kJ /<br> 513 kcal or on two rows!
                            e_str = cols[col_100].lower().replace('/', '')
                            
                            m = re.search(r'(\d+)\s*kcal', e_str)
                            if m:
                                kcal = m.group(1)                                
                                self.nutrition_info[n_type] = int(kcal)
                            else:
                                print(f"\tenergy: NO MATCH:{e_str}")
                                if 'kj' in e_str:                                    
                                    kj_to_kcal = e_str.replace('kj','').strip()
                                    kj_to_kcal = int(float(kj_to_kcal) * 0.239006)
                                    self.nutrition_info[n_type] = int(kj_to_kcal)
                        else:
                            self.nutrition_info[n_type] = remove_g_and_less_than(cols[col_100])
            
            pprint(self.nutrition_info)
            
        except StopIteration as exp:
            print(exp)
            print('ERROR processing nutrition table - NOT found!')
        
        print('- - - - - - - nutrition - - - - - - - E')

        # sbs            
        # self.supplier_item_code = ''
        # <p class="pd__item-code">Item code: <span id="productSKU">952811</span></p>        
        # try:
        #     e = driver.find_element(*query['supplier_item_code'][cur])
        #     self.supplier_item_code = e.text.strip()
        # except Exception as exp:
        #     print(exp.msg)
        #     print('self.supplier_item_code NOT found!')                    
            
        self.supplier_name      = 'Tesco'

    def scrape_asda(self):
        print(f"scraping ASDA: {self.product_url}")     

        # - - - - Helpers factor out where generic - - - S
        # TODO factor out
        LIST = 0    # TODO get rid of manual specifier detect list/string act accordingly
        HTML = 1    # back port to previous versions
        def get_nutr_per_100g_col(table_header, header_type=HTML):
            default_col=1
            col_100 = None
            head_cols = []

            if header_type == HTML:
                head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',table_header.get_attribute('innerHTML'), re.S)
            elif header_type == LIST:
                head_cols = table_header

            for col,text in enumerate(head_cols):
                col_100 = col
                if re.search(r'100[gml]+', text): return(col_100)

            return(default_col)
        
        # replace 2,2 w/ 2.2
        # replace (2,2) w/ 2.2
        # convert mg & ug into g
        def remove_g_and_less_than(str_g: str) -> float:
            str_g = str_g.lower()
            multiplier = 1

            # TODO switch code so it uses ug as standard unit
            if 'mg' in str_g:
                str_g = str_g.replace('mg', '')
                multiplier = 1.0 / 1000.0

            if ('mcg' in str_g) or ('μg' in str_g) or ('ug' in str_g):
                str_g = str_g.replace('mcg', '').replace('μg', '').replace('ug', '')
                multiplier = 1.0 / 1000000.0                
            
            str_g = str_g.replace('g', '').replace('(', '').replace(')', '').replace(',', '.').replace('trace', '0.01')

            if '&lt;' in str_g or '<' in str_g:        
                str_g = str_g.replace('&lt;', '').replace('<', '')
            
                return round(float(str_g) * multiplier * 0.8, 2)
            
            return round(float(str_g) * multiplier, 2)   
        # - - - - Helpers factor out where generic - - - E
        
        # register driver
        if ProductInfo.asd_driver == None:
            ProductInfo.asd_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.asd_driver

        DSK = 0
        MOB = 1
        BY  = 0
        SEL = 1
        cur = DSK
        query = {
            'cookie_b':             [(By.CSS_SELECTOR, '#onetrust-accept-btn-handler'),
                                     (By.CSS_SELECTOR, '#onetrust-accept-btn-handler')],
            'product_title':        [(By.CSS_SELECTOR, '.pdp-main-details > div'),
                                     (By.CSS_SELECTOR, '.pdp-main-details > div')],
            'package_qty_str':      [(By.CSS_SELECTOR,'.pdp-main-details__weight'),
                                     (By.CSS_SELECTOR,'.pdp-main-details__weight')],                                     
            'price_per_package':    [(By.CSS_SELECTOR, '.pdp-main-details__price-container'),
                                     (By.CSS_SELECTOR, '.pdp-main-details__price-container')],
            'price_per_measure':    [(By.CSS_SELECTOR, '.pdp-main-details__price-and-uom .co-product__price-per-uom'),
                                     (By.CSS_SELECTOR, '.pdp-main-details__price-and-uom .co-product__price-per-uom')],
            'item_info':            [(By.CSS_SELECTOR, '.pdp-description-reviews__product-details-title, .pdp-description-reviews__product-details-content'),
                                     (By.CSS_SELECTOR, '.pdp-description-reviews__product-details-title, .pdp-description-reviews__product-details-content')], # Gets Description but misses i_string / allergies
            'nutri_table':          [(By.CSS_SELECTOR, '.pdp-description-reviews__nutrition-table-cntr > div'), # NOT table!!
                                     (By.CSS_SELECTOR, '.pdp-description-reviews__nutrition-table-cntr > div')],
            
            # '':[(,),(,)],
        }
        item_info = {
            #'description': [],
            'features': [],
            'ingredients': [],
            #'dietary information': [],
            #'allergy information': [],  
            'allergy advice': [],
            'additives': [],
            #'number of uses': [],
            #'net contents': [],
            #'net content': [],
            'life style': []
        }

        # for desktop replace [DSK] for [MOB] for mobile
        # (query['cookie_b'][DSK][BY], query['cookie_b'][DSK][SEL])
        # or
        # query['cookie_b'][cur] where cur = DSK or MOB
        # WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][DSK])).click()

        # remove cookie request
        cookie_btn_timeout_inSec = 5  
        driver.get(self.product_url)

        if ProductInfo.asd_cookie_barrier:
            try:
                print(f'try cookie_button w WAIT: {cookie_btn_timeout_inSec}')
                WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][cur])).click()
                print('CLICKED cookie_button')
                ProductInfo.asd_cookie_barrier = False
            except TimeoutException:
                print("Loading took too much time!")

        # wait content load
        # TODO H - get info at same time as wait load
        # selector
        h_tags = h2_tags = ''
        delay_in_seconds = 1
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:
            print(f'# # #> waiting for Title & QTY CSS:')
            h_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
            h_tags = h_tags.text.strip()
            print(f'# # #> found h_tags:\n{h_tags}')
        except TimeoutException:
            print("# # # TIMEOUT> Waiting for Title took too much time!")
            cur = MOB if cur == DSK else MOB
        except Exception as exp:
            print(exp.msg)
            print('Title NOT FOUND')
            cur = MOB if cur == DSK else MOB
        
        if not h_tags:
            print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
            try:            
                print(f'# # #> waiting for Title & QTY XPATH:')
                h2_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
                h2_tags = h2_tags.text.strip()
                print(f'# # #> found h2_tags:\n{h2_tags}')
            except TimeoutException:
                print(f'# # # TIMEOUT> waiting for Title & QTY XPATH:')
            except Exception as exp:
                print(exp.msg)
                print('Title NOT FOUND - h2_tags')

        
        # self.product_name             British Semi Skimmed Milk
        # self.package_qty_str          (1.13L) 2 pint
        # self.alt_package_in_g         1130 grams
        #      
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        product_title = ''
        try:

            if h_tags or h2_tags:
                product_title = h_tags if h_tags else h2_tags 
                print(f"[self.product_name] {self.product_name} < h_tags {h_tags}<  h2_tags {h2_tags}<")
            else:
                try:
                    print(f"[self.product_name] {self.product_name} < * * * NO h_tags or h2_tags * * *")
                    e = driver.find_element(*query['product_title'][cur])
                    product_title = e.text.strip()                
                except Exception as exp:
                    print(exp.msg)
                    print('self.product_name NOT found! no h / h2 / or retry')

            product_title_sections = product_title.split('\n')
            self.product_name = product_title_sections[0].strip() +' ' + product_title_sections[1].strip()
            self.supplier_item_code = product_title_sections[5].replace('Product code:','').strip()

            # remove multipack X no
            multibuy_rgx = r'(\d+)\s*x'
            m = re.search(multibuy_rgx, self.product_name, re.I)
            if m:
                product_name_multiby_removed = self.product_name.replace(m.group(0), '')
                self.multipack_qty = m.group(1)
            else:
                product_name_multiby_removed = self.product_name

            # in case there is no size specified get size from product name            
            alt_package_in_g_rgx = r'(([\.\d]+)\s*(Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|Grams|L|l)\s*(?:(\/)?\d+\s*Pint(?:s)?)?)'
            m = re.search(alt_package_in_g_rgx, product_name_multiby_removed, re.I)
            if m:
                self.package_qty_str = m.group(1)
                self.units = m.group(3)
                self.qty = round(float(m.group(2).strip()),2)
                self.convert_pkg_str_to_qty_in_g() # alt_package_in_g <- None if units is Pack / Loose
                print(f"INFO FROM TITLE  - - - - - - - - : S [self.package_qty_str] - {self.package_qty_str} <")
                print(f"self.product_name: {self.product_name}<")
                print(f"self.package_qty_str: {self.package_qty_str}<")
                print(f"self.package_in_g: {self.package_in_g}<")
                print(f"self.alt_package_in_g: {self.alt_package_in_g}<")
                print(f"self.units: {self.units}<")
                print(f"self.qty: {self.qty}<")
                print(f"self.no_of_each: {self.no_of_each}<")
                print("INFO FROM TITLE  - - - - - - - - : E")
            
        except Exception as exp:
            print(exp.msg)
            print('self.product_name NOT found!')         
        
        # self.price_per_package            £5.50 £2.21/kg  - can appear together
        #                                     ^^
        # self.price_per_package    in      
        # self.price_per_measure    in      
        print(f"\n\nquery['price_per_package'][{cur}] {query['price_per_package'][cur]}")
        try:
            #css_selector = '.price-per-sellable-unit'
            e = driver.find_element(*query['price_per_package'][cur])
            self.price_per_package = e.text.strip().replace('now\n','')
            # m = re.match(r'£(\d+.\d\d)[^\/]', f"{e.text.strip()} ", re.M)       # match price NOT price/unit
            # if m:
            #     self.price_per_package = m.group(1)
            self.package_in_g = 99999999
            print(f"£/pkg: {self.price_per_package} [self.price_per_package] from >{e.text.strip()}<")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_package NOT found!')

        
        print(f"\n\nquery['price_per_measure'][{cur}] {query['price_per_measure'][cur]}")
        try:
            #css_selector = '.price-per-quantity-weight'
            e = driver.find_element(*query['price_per_measure'][cur])            
            self.price_per_measure = e.text.strip().replace('(','').replace(')','')
            print(f"£/unit: {self.price_per_measure} [self.price_per_measure]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_measure NOT found!')

        # Product Description (TODO) & Infomation
        # document.querySelectorAll('h2.product-info-block__title')
        # gives description and 
        # 
        # all rest under Information
        #
        # more generic gives all info blocks except nutrition (whic we already have)
        # document.querySelectorAll('div.product-info-block')

        # >>> list = driver.find_elements(By.CSS_SELECTOR,'div.product-info-block, .product-info-block__content')

        print(f"\n\nquery['item_info'][{cur}] {query['item_info'][cur]}")

        e_list = []
        try:            
            e_list = driver.find_elements(*query['item_info'][cur]) 
        except Exception as exp:
            print(exp.msg)
            #pprint(exp)
            print('ERROR processing item_info PAIRS - NOT found!')

        item_info_markers = list(item_info.keys())

        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - S')
        # skip on fin=d
        i = 0
        while i < len(e_list):
            elmnt = e_list[i]
            found_mk = None
            for marker in item_info_markers:
                print(f"\n{i:02} - {elmnt.text.lower()} - Mkr: {marker}")
                if i+1 < len(e_list): print(f"{i+1:02} - {e_list[i+1]}\n{e_list[i+1].text}")
                if marker == elmnt.text.lower().strip():
                    item_info[marker].append(e_list[i+1].text)
                    print(f"STORE:{i:02}[{marker}] {elmnt.text} <")
                    print(f"item_info[{marker}]:{item_info[marker]} <") 
                    found_mk = marker
                    i += 1  # skip next index
                    break
            if found_mk: item_info_markers.remove(found_mk)
            i += 1
        print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - E')


        print('+>> item_info - - - - - - - - - - - - - - - - - - - S')
        pprint(item_info)
        print('+>> item_info - - - - - - - - - - - - - - - - - - - E')
                
        # Pack size in Product Description - TODO L 
        # Net Contents also has same info ? multibuy
        if ('net content' in item_info) and (len(item_info['net content']) > 0):     # not always present
            self.package_in_g = item_info['net content'][0]
        else:
            self.package_in_g = self.alt_package_in_g
        
        print('ingredients  - - - - - - - - S')
        print(f"len(item_info['ingredients']) {len(item_info['ingredients'])}")
        print(f"item_info['ingredients'] {item_info['ingredients']} <")
                                                # TODO scan for water salt oil and only other ingredients - cashews, smoke mackerel
        if len(item_info['ingredients']) == 0:  # if no ingredient assume atomic roqufort, milk, smoked mackerel
            print(f"NO INGREDIENT FOUND: {item_info['ingredients']} <")
            self.i_text = ''
            self.igdt_type = 'atomic'            
        else:
            self.i_text = item_info['ingredients'][0]
            ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.i_text, self.ri_name)
            self.allergens = ots_info['allergens']
            print(f"- - - - - - - ots_info")
            pprint(ots_info)
            self.i_list = ots_info['i_list']
            if len(self.i_list) == 1: 
                print(f"ATOMIC: len(self.i_list) [{len(self.i_list)}]\n{self.i_list}\nself.i_text: {self.i_text}")
                self.igdt_type = 'atomic'
            else:
                self.igdt_type = 'ots'  # override ctor atomic
        
        # product may have been set atomic by args passed to constructor/init
        if self.igdt_type == 'atomic':
            print(f"- - -: * * * {self.ri_name} - ATOMIC . . . .  self.i_text = '__igdts__'\n self.i_text was: {self.i_text} <")
            self.i_text = '__igdts__'


        # update allergens from scrape info - tsc
        #if (len(item_info['allergy information']) > 0): self.allergens_raw = item_info['allergy information'][0] # tsc       
        if (len(item_info['allergy advice']) > 0): self.allergens_raw = item_info['allergy advice'][0] # mrs

        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.allergens_raw, self.ri_name)
        
        print(f"processing self.allergens_raw[{self.allergens_raw}] = [{ots_info['allergens']}]")
        
        self.allergens.update(ots_info['allergens'])
        if (self.igdt_type == 'atomic') and (len(self.allergens)) and (self.i_text == '__igdts__'):
            self.i_text = f"{self.ri_name}, (contains {', '.join(self.allergens)})"

        print('ingredients  - - - - - - - - E')        
        
        if 'product description' in item_info:      
            # TODO need to process/accumulate down to 'Information' and pull out Pack size if present
            self.product_desc = item_info['product description']



        print('- - - - - - - nutrition DIV type - - - - - - - S')

        
        # item_info['nutrition']
        nut_regex = ProductInfo.nutrition_symbol_to_regex
        row_data = []
        col_100 = 1

        # tb_rows = driver.find_elements(By.CSS_SELECTOR, '.pdp-description-reviews__nutrition-table-cntr > div')
        # if tb_rows:
        #     for row in tb_rows:
        #         cells = row.find_elements(By.CSS_SELECTOR, '.pdp-description-reviews__nutrition-cell')
        #         cell_data = [cell.text for cell in cells]
        #         row_data.append(cell_data)
        
        # print('- - - - - - - DIV rows S') # TODO remove
        # pprint(row_data)
        # print('- - - - - - - DIV rows E')

        # nutrition table - - - - NOT WORKING: for DIV style
        try:
            tb_rows = driver.find_elements(*query['nutri_table'][cur])
            if tb_rows:
                for row in tb_rows:
                    cells = row.find_elements(By.CSS_SELECTOR, '.pdp-description-reviews__nutrition-cell')
                    cell_data = [cell.text for cell in cells]
                    row_data.append(cell_data)

            rows = iter(row_data)
            tb_head = next(rows)    # first row always col titles
            #head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S) # TODO REMOVE
            
            col_100 = get_nutr_per_100g_col(tb_head, LIST)
            
            for cols in rows:
                print(f"\n-R: {cols}")
                for n_type, n_regex in nut_regex.items():
                    if re.search(n_regex, cols[0].lower()):
                        #self.nutrition_info[n_type] = cols[col_100]
                        if n_type == 'energy':
                            # in single row:  2143 kJ /<br> 513 kcal or on two rows!
                            e_str = cols[col_100].lower().replace('/', '')
                            
                            m = re.search(r'(\d+)\s*kcal', e_str)
                            if m:
                                kcal = m.group(1)                                
                                self.nutrition_info[n_type] = int(kcal)
                            elif 'kcal' in cols[0].lower(): # check title for kcal
                                self.nutrition_info[n_type] = int(cols[col_100].lower())
                            else:
                                print(f"\tenergy: NO MATCH:{e_str}")
                                if 'kj' in e_str:                                    
                                    kj_to_kcal = e_str.replace('kj','').strip()
                                    kj_to_kcal = int(float(kj_to_kcal) * 0.239006)
                                    self.nutrition_info[n_type] = int(kj_to_kcal)
                        else:
                            self.nutrition_info[n_type] = remove_g_and_less_than(cols[col_100])
            
            pprint(self.nutrition_info)
            
        except StopIteration as exp:
            print(exp)
            print('ERROR processing nutrition table - NOT found!')




        print('- - - - - - - nutrition DIV type - - - - - - - E')

        # sbs            
        # self.supplier_item_code = ''
        # <p class="pd__item-code">Item code: <span id="productSKU">952811</span></p>        
        # try:
        #     e = driver.find_element(*query['supplier_item_code'][cur])
        #     self.supplier_item_code = e.text.strip()
        # except Exception as exp:
        #     print(exp.msg)
        #     print('self.supplier_item_code NOT found!')                    
            
        self.supplier_name      = 'Asda'        

    def scrape_waitrose(self):
        print(f"scraping WAITROSE: {self.product_url}")      

        # - - - - Helpers factor out where generic - - - S
        # TODO factor out
        LIST = 0    # TODO get rid of manual specifier detect list/string act accordingly
        HTML = 1    # back port to previous versions
        def get_nutr_per_100g_col(table_header, header_type=HTML):
            default_col=1
            col_100 = None
            head_cols = []

            if header_type == HTML:
                head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',table_header.get_attribute('innerHTML'), re.S)
            elif header_type == LIST:
                head_cols = table_header

            for col,text in enumerate(head_cols):
                col_100 = col
                if re.search(r'100[gml]+', text): return(col_100)

            return(default_col)
        
        # replace 2,2 w/ 2.2
        # replace (2,2) w/ 2.2
        # convert mg & ug into g
        def remove_g_and_less_than(str_g: str) -> float:
            str_g = str_g.lower()
            multiplier = 1

            # TODO switch code so it uses ug as standard unit
            if 'mg' in str_g:
                str_g = str_g.replace('mg', '')
                multiplier = 1.0 / 1000.0

            if ('mcg' in str_g) or ('μg' in str_g) or ('ug' in str_g):
                str_g = str_g.replace('mcg', '').replace('μg', '').replace('ug', '')
                multiplier = 1.0 / 1000000.0                
            
            str_g = str_g.replace('g', '').replace('(', '').replace(')', '').replace(',', '.').replace('trace', '0.01')

            if '&lt;' in str_g or '<' in str_g:        
                str_g = str_g.replace('&lt;', '').replace('<', '')
            
                return round(float(str_g) * multiplier * 0.8, 2)
            
            return round(float(str_g) * multiplier, 2)     
        # - - - - Helpers factor out where generic - - - E
        
        # register driver
        if ProductInfo.wtr_driver == None:
            ProductInfo.wtr_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.wtr_driver

        DSK = 0
        MOB = 1
        BY  = 0
        SEL = 1
        cur = DSK
        query = {
            'cookie_b':             [(By.CSS_SELECTOR, '.acceptAll___CHGcH'),
                                     (By.CSS_SELECTOR, '.acceptAll___CHGcH')],
            'product_title':        [(By.CSS_SELECTOR, '.name___XT_RE'),
                                     (By.CSS_SELECTOR, '#productName')],
            'package_qty_str':      [(By.CSS_SELECTOR,'.sizeMessage___VhEEO'),
                                     (By.CSS_SELECTOR,'.sizeMessage___VhEEO')],                                     
            'price_per_package':    [(By.CSS_SELECTOR, 'span[data-test="product-page-price"] > span'),
                                     (By.CSS_SELECTOR, 'span[data-test="product-page-price"] > span')],
            'price_per_measure':    [(By.CSS_SELECTOR, '.pricePerUnit___c9Vo4'),
                                     (By.CSS_SELECTOR, '.pricePerUnit___c9Vo4')],
            'item_info':            [(By.CSS_SELECTOR, 'h3'),
                                     (By.CSS_SELECTOR, 'h3')],
            'ingredients':          [(By.CSS_SELECTOR, '.ingredientsText___IvfUB > p'), 
                                     (By.CSS_SELECTOR, '.ingredientsText___IvfUB > p')],                                     
            'nutri_table':          [(By.CSS_SELECTOR, '.nutrition___VCHp1 .table.table-striped tr'), 
                                     (By.CSS_SELECTOR, '.nutrition___VCHp1 .table.table-striped tr')],            
            # '':[(,),(,)],
        }
        item_info = {
            #'description': [],
            'features': [],
            'ingredients': [],
            #'dietary information': [],
            #'allergy information': [],  
            'allergy advice': [],
            'additives': [],
            #'number of uses': [],
            #'net contents': [],
            #'net content': [],
            'life style': []
        }

        # for desktop replace [DSK] for [MOB] for mobile
        # (query['cookie_b'][DSK][BY], query['cookie_b'][DSK][SEL])
        # or
        # query['cookie_b'][cur] where cur = DSK or MOB
        # WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][DSK])).click()

        # remove cookie request
        cookie_btn_timeout_inSec = 5  
        driver.get(self.product_url)

        if ProductInfo.wtr_cookie_barrier:
            try:
                print(f'try cookie_button w WAIT: {cookie_btn_timeout_inSec}')
                WebDriverWait(driver, cookie_btn_timeout_inSec).until(EC.element_to_be_clickable(query['cookie_b'][cur])).click()
                print('CLICKED cookie_button')
                ProductInfo.wtr_cookie_barrier = False
            except TimeoutException:
                print("Loading took too much time!")

        # wait content load
        # TODO H - get info at same time as wait load
        # selector
        h_tags = h2_tags = ''
        delay_in_seconds = 1
        print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        try:
            print(f'# # #> waiting for Title & QTY CSS:')
            h_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
            h_tags = h_tags.text.strip()
            print(f'# # #> found h_tags:\n{h_tags}')
            self.product_name = h_tags
        except TimeoutException:
            print("# # # TIMEOUT> Waiting for Title took too much time!")
            cur = MOB if cur == DSK else MOB
        except Exception as exp:
            print(exp.msg)
            print('Title NOT FOUND')
            cur = MOB if cur == DSK else MOB
        
        if not h_tags:
            print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
            try:            
                print(f'# # #> waiting for Title & QTY XPATH:')
                h2_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located(query['product_title'][cur]))
                h2_tags = h2_tags.text.strip()
                self.product_name = h2_tags
                print(f'# # #> found h2_tags:\n{h2_tags}')
            except TimeoutException:
                print(f'# # # TIMEOUT> waiting for Title & QTY XPATH:')
            except Exception as exp:
                print(exp.msg)
                print('Title NOT FOUND - h2_tags')

        
        # # self.product_name             British Semi Skimmed Milk
        # # self.package_qty_str          (1.13L) 2 pint
        # # self.alt_package_in_g         1130 grams
        # #      
        # print(f"\n\nquery['product_title'][{cur}] {query['product_title'][cur]}")
        # product_title = ''
        # try:

        #     if h_tags or h2_tags:
        #         product_title = h_tags if h_tags else h2_tags 
        #         print(f"[self.product_name] {self.product_name} < h_tags {h_tags}<  h2_tags {h2_tags}<")
        #     else:
        #         try:
        #             print(f"[self.product_name] {self.product_name} < * * * NO h_tags or h2_tags * * *")
        #             e = driver.find_element(*query['product_title'][cur])
        #             product_title = e.text.strip()                
        #         except Exception as exp:
        #             print(exp.msg)
        #             print('self.product_name NOT found! no h / h2 / or retry')

        #     product_title_sections = product_title.split('\n')
        #     self.product_name = product_title_sections[0].strip() +' ' + product_title_sections[1].strip()
        #     self.supplier_item_code = product_title_sections[5].replace('Product code:','').strip()

        #     # remove multipack X no
        #     # multibuy_rgx = r'(\d+)\s*x'
        #     # m = re.search(multibuy_rgx, self.product_name, re.I)
        #     # if m:
        #     #     product_name_multiby_removed = self.product_name.replace(m.group(0), '')
        #     #     self.multipack_qty = m.group(1)
        #     # else:
        #     #     product_name_multiby_removed = self.product_name

        #     # in case there is no size specified get size from product name            
        #     # alt_package_in_g_rgx = r'(([\.\d]+)\s*(Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|Grams|L|l)\s*(?:(\/)?\d+\s*Pint(?:s)?)?)'
        #     # m = re.search(alt_package_in_g_rgx, product_name_multiby_removed, re.I)
        #     # if m:
        #     #     self.package_qty_str = m.group(1)
        #     #     self.units = m.group(3)
        #     #     self.qty = round(float(m.group(2).strip()),2)
        #     #     self.convert_pkg_str_to_qty_in_g() # alt_package_in_g <- None if units is Pack / Loose
        #     #     print(f"INFO FROM TITLE  - - - - - - - - : S [self.package_qty_str] - {self.package_qty_str} <")
        #     #     print(f"self.product_name: {self.product_name}<")
        #     #     print(f"self.package_qty_str: {self.package_qty_str}<")
        #     #     print(f"self.package_in_g: {self.package_in_g}<")
        #     #     print(f"self.alt_package_in_g: {self.alt_package_in_g}<")
        #     #     print(f"self.units: {self.units}<")
        #     #     print(f"self.qty: {self.qty}<")
        #     #     print(f"self.no_of_each: {self.no_of_each}<")
        #     #     print("INFO FROM TITLE  - - - - - - - - : E")
            
        # except Exception as exp:
        #     print(exp.msg)
        #     print('self.product_name NOT found!')         


        print(f"\n\nquery['package_qty_str'][{cur}] {query['package_qty_str'][cur]}")
        try:
            e = driver.find_element(*query['package_qty_str'][cur])
            self.package_qty_str = e.text.strip() #.replace('now\n','')

            alt_package_in_g_rgx = r'(([\.\d]+)\s*(Litre|Loose|Pack|mg|Kg|Ml|ml|g|G|Grams|L|l)\s*(?:(\/)?\d+\s*Pint(?:s)?)?)'
            m = re.search(alt_package_in_g_rgx, self.package_qty_str, re.I)
            if m:
                self.package_qty_str = m.group(1)
                self.units = m.group(3)
                self.qty = round(float(m.group(2).strip()),2)
                self.convert_pkg_str_to_qty_in_g() # alt_package_in_g <- None if units is Pack / Loose
                print(f"INFO FROM TITLE  - - - - - - - - : S [self.package_qty_str] - {self.package_qty_str} <")
                print(f"self.product_name: {self.product_name}<")
                print(f"self.package_qty_str: {self.package_qty_str}<")
                print(f"self.package_in_g: {self.package_in_g}<")
                print(f"self.alt_package_in_g: {self.alt_package_in_g}<")
                print(f"self.units: {self.units}<")
                print(f"self.qty: {self.qty}<")
                print(f"self.no_of_each: {self.no_of_each}<")
                print("INFO FROM TITLE  - - - - - - - - : E")

            print(f"Pkg QTY: {self.package_qty_str} [self.package_qty_str] from >{e.text.strip()}<")
        except Exception as exp:
            print(exp.msg)
            print('self.package_qty_str NOT found!')

        # self.price_per_package            £5.50 £2.21/kg  - can appear together
        #                                     ^^
        # self.price_per_package    in      
        # self.price_per_measure    in      
        print(f"\n\nquery['price_per_package'][{cur}] {query['price_per_package'][cur]}")
        try:
            #css_selector = '.price-per-sellable-unit'
            e = driver.find_element(*query['price_per_package'][cur])
            self.price_per_package = e.text.strip().replace('now\n','')
            # m = re.match(r'£(\d+.\d\d)[^\/]', f"{e.text.strip()} ", re.M)       # match price NOT price/unit
            # if m:
            #     self.price_per_package = m.group(1)
            self.package_in_g = 99999999
            print(f"£/pkg: {self.price_per_package} [self.price_per_package] from >{e.text.strip()}<")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_package NOT found!')

        
        print(f"\n\nquery['price_per_measure'][{cur}] {query['price_per_measure'][cur]}")
        try:
            #css_selector = '.price-per-quantity-weight'
            e = driver.find_element(*query['price_per_measure'][cur])            
            self.price_per_measure = e.text.strip().replace('(','').replace(')','')
            print(f"£/unit: {self.price_per_measure} [self.price_per_measure]")
        except Exception as exp:
            print(exp.msg)
            print('self.price_per_measure NOT found!')

        # Product Description (TODO) & Infomation
        # document.querySelectorAll('h2.product-info-block__title')
        # gives description and 
        # 
        # all rest under Information
        #
        # more generic gives all info blocks except nutrition (whic we already have)
        # document.querySelectorAll('div.product-info-block')

        # >>> list = driver.find_elements(By.CSS_SELECTOR,'div.product-info-block, .product-info-block__content')

        print(f"\n\nquery['item_info'][{cur}] {query['item_info'][cur]}")

        e_list = []
        try:            
            e_list = driver.find_elements(*query['item_info'][cur]) 
        except Exception as exp:
            print(exp.msg)
            #pprint(exp)
            print('ERROR processing item_info PAIRS - NOT found!')

        item_info_markers = list(item_info.keys())

        # print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - S')
        # # skip on fin=d
        # i = 0
        # while i < len(e_list):
        #     elmnt = e_list[i]
        #     found_mk = None
        #     for marker in item_info_markers:
        #         print(f"\n{i:02} - {elmnt.text.lower()} - Mkr: {marker}")
        #         if i+1 < len(e_list): print(f"{i+1:02} - {e_list[i+1]}\n{e_list[i+1].text}")
        #         if marker == elmnt.text.lower().strip():
        #             item_info[marker].append(e_list[i+1].text)
        #             print(f"STORE:{i:02}[{marker}] {elmnt.text} <")
        #             print(f"item_info[{marker}]:{item_info[marker]} <") 
        #             found_mk = marker
        #             i += 1  # skip next index
        #             break
        #     if found_mk: item_info_markers.remove(found_mk)
        #     i += 1
        # print('while i < len(e_list):: - - - - - - - - - - - - - - - - - - - - - - - - E')


        print('+>> item_info - - - - - - - - - - - - - - - - - - - S')
        pprint(item_info)
        print('+>> item_info - - - - - - - - - - - - - - - - - - - E')
                
        # Pack size in Product Description - TODO L 
        # Net Contents also has same info ? multibuy
        # if ('net content' in item_info) and (len(item_info['net content']) > 0):     # not always present
        #     self.package_in_g = item_info['net content'][0]
        # else:
        #     self.package_in_g = self.alt_package_in_g
        
        print('ingredients  - - - - - - - - S')
        print(f"\n\nquery['ingredients'][{cur}] {query['ingredients'][cur]}")
        try:
            i_element = driver.find_element(*query['ingredients'][cur])
            item_info['ingredients'] = [i_element.get_attribute("textContent")]
        except NoSuchElementException:
            item_info['ingredients'] = []

        print(f"len(item_info['ingredients']) {len(item_info['ingredients'])}")
        print(f"item_info['ingredients'] {item_info['ingredients']} <")
                                                # TODO scan for water salt oil and only other ingredients - cashews, smoke mackerel
        if len(item_info['ingredients']) == 0:  # if no ingredient assume atomic roqufort, milk, smoked mackerel
            print(f"NO INGREDIENT FOUND: {item_info['ingredients']} <")
            self.i_text = ''
            self.igdt_type = 'atomic'            
        else:
            self.i_text = item_info['ingredients'][0]
            ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.i_text, self.ri_name)
            self.allergens = ots_info['allergens']
            print(f"- - - - - - - ots_info")
            pprint(ots_info)
            self.i_list = ots_info['i_list']
            if len(self.i_list) == 1: 
                print(f"ATOMIC: len(self.i_list) [{len(self.i_list)}]\n{self.i_list}\nself.i_text: {self.i_text}")
                self.igdt_type = 'atomic'
            else:
                self.igdt_type = 'ots'  # override ctor atomic
        
        # product may have been set atomic by args passed to constructor/init
        if self.igdt_type == 'atomic':
            print(f"- - -: * * * {self.ri_name} - ATOMIC . . . .  self.i_text = '__igdts__'\n self.i_text was: {self.i_text} <")
            self.i_text = '__igdts__'


        # update allergens from scrape info - tsc
        #if (len(item_info['allergy information']) > 0): self.allergens_raw = item_info['allergy information'][0] # tsc       
        if (len(item_info['allergy advice']) > 0): self.allergens_raw = item_info['allergy advice'][0] # mrs

        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(self.allergens_raw, self.ri_name)
        
        print(f"processing self.allergens_raw[{self.allergens_raw}] = [{ots_info['allergens']}]")
        
        self.allergens.update(ots_info['allergens'])
        if (self.igdt_type == 'atomic') and (len(self.allergens)) and (self.i_text == '__igdts__'):
            self.i_text = f"{self.ri_name}, (contains {', '.join(self.allergens)})"

        print('ingredients  - - - - - - - - E')        
        
        if 'product description' in item_info:      
            # TODO need to process/accumulate down to 'Information' and pull out Pack size if present
            self.product_desc = item_info['product description']



        print('- - - - - - - nutrition - - - - - - - S')
        # <table class="nutritionTable">
        #     <thead>
        #         <tr class="tableTitleRow">
        #         <th scope="col">Typical Values
        #         (cooked as per instructions)</th><th scope="col">Per 100g&nbsp;</th><th scope="col">Per 80g serving&nbsp;</th><th scope="col">% based on RI for Average Adult</th>
        #         </tr>
        #     </thead>
        #     <tbody>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader" rowspan="2">Energy</th><td class="tableRow1">477kJ</td><td class="tableRow1">381kJ</td><td class="tableRow1">-</td>
        #         </tr>
        #         <tr class="tableRow0">
        #             <td class="tableRow0">113kcal</td><td class="">90kcal</td><td class="">5%</td>
        #         </tr>
        #         <tr class="tableRow1">
        #             <th scope="row" class="rowHeader">Fat</th><td class="tableRow1">&lt;0.5g</td><td class="nutritionLevel1">&lt;0.5g</td><td class="nutritionLevel1">1%</td>
        #         </tr>
        #     </tbody>
        # </table>
        
        # item_info['nutrition']
        nut_regex = ProductInfo.nutrition_symbol_to_regex
        row_data = []
        col_100 = 1

        # nutrition table - - - - WORKING: on both layouts
        try:
            tb_rows = driver.find_elements(*query['nutri_table'][cur])
            rows = iter(tb_rows)
            tb_head = next(rows)    # first row always col titles
            head_cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',tb_head.get_attribute('innerHTML'), re.S) # TODO REMOVE
            
            col_100 = get_nutr_per_100g_col(tb_head)
            
            print(f"--H: {head_cols}")
            for row in rows:
                cols = re.findall(r'<t[hd].*?>(.*?)<\/t[hd]>',row.get_attribute('innerHTML'))
                print(f"-R: {cols}")
                row_data.append(cols)   # TODO is this even used? WHERE? REMOVE - 4 occurences
                for n_type, n_regex in nut_regex.items():
                    if re.search(n_regex, cols[0].lower()):
                        #self.nutrition_info[n_type] = cols[col_100]
                        if n_type == 'energy':
                            # in single row:  2143 kJ /<br> 513 kcal or on two rows!
                            e_str = cols[col_100].lower().replace('/', '')
                            
                            m = re.search(r'(\d+)\s*kcal', e_str)
                            if m:
                                kcal = m.group(1)                                
                                self.nutrition_info[n_type] = int(kcal)
                            else:
                                print(f"\tenergy: NO MATCH:{e_str}")
                                if 'kj' in e_str:                                    
                                    kj_to_kcal = e_str.replace('kj','').strip()
                                    kj_to_kcal = int(float(kj_to_kcal) * 0.239006)
                                    self.nutrition_info[n_type] = int(kj_to_kcal)
                        else:
                            self.nutrition_info[n_type] = remove_g_and_less_than(cols[col_100])
            
            pprint(self.nutrition_info)
            
        except StopIteration as exp:
            print(exp)
            print('ERROR processing nutrition table - NOT found!')
        
        print('- - - - - - - nutrition - - - - - - - E')

        # sbs            
        # self.supplier_item_code = ''
        # <p class="pd__item-code">Item code: <span id="productSKU">952811</span></p>        
        # try:
        #     e = driver.find_element(*query['supplier_item_code'][cur])
        #     self.supplier_item_code = e.text.strip()
        # except Exception as exp:
        #     print(exp.msg)
        #     print('self.supplier_item_code NOT found!')                    
            
        self.supplier_name      = 'Waitrose' 

    def scrape_coop(self):
        print(f"scraping COOP: {self.product_url}")
      
    def scrape_ocado(self):
        print(f"scraping OCADO: {self.product_url}")
      
    def scrape_booker(self):
        print(f"scraping BOOKER: {self.product_url}")
      
    def scrape_aldi(self):
        print(f"scraping ALDI: {self.product_url}")
      
    def scrape_specialist(self):
        print(f"scraping WHO KNEW!?: {self.product_url}")
      
        
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # top level get nutrient request
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_product_info(self):
      
        # specialise this 
        # driver = webdriver.Chrome('chromedriver')
        # cookie_barrier = True
        # delay_in_seconds = 3    
        # driver.get(url)
      
        supplier_regex = [  
          r'(sainsburys)',  # sbs
          r'(morrisons)',   # mrs
          r'(tesco)',       # tsc
          r'(waitrose)',    # wtr
          r'(coop)',        # cop
          r'(asda)',        # asd
          r'(ocado)',       # ocd
          r'(booker)',      # bkr
          r'(aldi)'         # ald
        ]
        
        match = None                    # TODO upgrade python to 3.10 for switch case (match)
        for r in supplier_regex:
            print(f"CHECKING URL to decide SUPPLIER:\n{self.product_url}")
            m = re.search(r, self.product_url)            
            if m:
              match = m.group(1)
              break

        if match == 'sainsburys':
            self.scrape_sainsburys()
          
        elif match == 'morrisons':
            self.scrape_morrisons()
          
        elif match == 'tesco':
            self.scrape_tesco()
          
        elif match == 'waitrose':
            self.scrape_waitrose()
          
        elif match == 'coop':
            self.scrape_coop()
          
        elif match == 'asda':
            self.scrape_asda()
          
        elif match == 'ocado':
            self.scrape_ocado()
        
        elif match == 'booker':
            self.scrape_booker()
        
        elif match == 'aldi':
            self.scrape_aldi()
        
        elif match == None:
            self.scrape_specialist()

     

    





                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# the rest is the RUBY original code
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                                                                                     #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #
                                                                                    #  
#   
#  
#  # Sainsburys
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_sainsburys #@product_page
#
#    @supplier_name = 'Sainsburys'
#    
#    #@product_name = @product_page.css("h1").text
#    @product_name = @product_page.search(".//h1[@class='pd__header']").text.strip 
#    puts "\n\nPRODUCT NAME: #{@product_name} <"
#    
#    @price_per_package = @product_page.search(".//p[@class='pricePerUnit']").text.strip  #> "95p/unit"
#    puts "Price per unit:  #{@price_per_package}"
#    
#    @price_per_measure = @product_page.search(".//p[@class='pricePerMeasure']").text.strip  #> "48p/100g"
#    puts "Price per measure:  #{@price_per_measure}"
#    
#    item_code_text = @product_page.search(".//p[@class='itemCode']").text.strip         #> "Item code: 1294231"
#    @supplier_item_code = item_code_text.sub('Item code:','').strip
#    puts "Item code:  #{@supplier_item_code}"
#    
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    # get_ingredients
#    
#    ingredient_search = @product_page.search(".//div[@class='itemTypeGroupContainer productText']//ul[@class='productIngredients']")
#
#    if ingredient_search                                      # make sure not None
#      
#      @ingredients_text = ingredient_search.text
#
#      text_to_process = @ingredients_text
#      
#      text_to_process.gsub!("\u00A0", " ")                    # replace non breaking space
#      
#      text_to_process.gsub!(".", "")                          # remove full stops
#      
#      @ingredients = text_to_process.split(',').collect{ |i| i.strip }  # collect into array
#           
#    end
#        
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    # nutrition_info_per_100g
#    
#    #table = @product_page.at('table') # moved to class='nutritionTable'
#    table = @product_page.search(".//table[@class='nutritionTable']")
#    pp table
#    puts "---@---"
#    puts table.text
#
#    # add header titles
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    #puts "Category".ljust(CATEGORY_WIDTH)+"Value".ljust(VALUE_WIDTH)
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#        
#    #table.search('tr').each { |tr|
#    #  puts "#{tr.children[1].text}".ljust(CATEGORY_WIDTH)+"#{tr.children[2].text}".ljust(VALUE_WIDTH)
#    #}
#    
#    nutrients = {}
#    
#    # find which column the per 100g/ml is    
#    col_100 = get_table_100g_colum(table, 2)
#    
#    table.search('tr').each { |tr|
#      title_column    = tr.children[1].text.downcase                        # specialise from morrison
#      quantity_column = '0'
#      quantity_column = tr.children[col_100].text.downcase unless tr.children[col_100] == None
#      
#      next if title_column =~ /per 100g/    # check here for 'as prepared'  # specialise from morrison
#      next if title_column =~ /servings/                                    # specialise from morrison
#      next if title_column =~ /reference/
#      
#      if quantity_column =~ @symbol_to_regex[:energy]
#        
#        nutrients[:energy] = (($1.to_f) / ENERGY_TO_KCAL).to_i
#        
#      end
#  
#      @symbol_to_regex.each_pair { |sym, regex|
#        
#        if title_column =~ regex
#          
#          quantity_column =~ /(\d+\.*\d*)\s*g/
#  
#          nutrients[sym] = $1.to_f.round(1)
#          
#        end
#  
#      }
#      
#      puts "#{title_column}".ljust(CATEGORY_WIDTH)+"#{quantity_column}".ljust(VALUE_WIDTH)
#    }
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    
#    #pp nutrients
#    
#    @nutrition_info = SimpleNutrientInfo.new  @nick_name, @product_name, @product_url, nutrients 
#    
#  end
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # Morrisons
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def get_morrison_ingredients
#    # refactor
#  end
#  
#  def scrape_morrisons #@product_page
#    @supplier_name = 'Morrisons'
#    
#    @product_name = @product_page.search(".//h1/strong[@itemprop='name']").text.strip 
#    #puts "\n\nPRODUCT NAME:        #{@product_name} - #{@supplier_name}"
#    
#    @price_per_package = @product_page.search(".//div[@class='typicalPrice']").text.strip
#    #puts "UNIT COST:           #{@price_per_package}"
#  
#    # Package weight:    ? - can be derived from unit cost & price/100g
#  
#    @price_per_measure = @product_page.search(".//p[@class='pricePerWeight']").text.strip
#    #puts "PRICE PER WEIGHT:    #{@price_per_measure}"
#    
#    @supplier_item_code = '-199' # define magic number 
#    
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    #get_morrison_ingredients
#    @ingredients_text = ''
#  
#    node_set = @product_page.search(".//div[@class='bopSection']")
#  
#    get_this_node = false
#  
#    # get the node after 'Allergy Advice'
#    node_set.search(".//p").each{ |node|
#          
#      if get_this_node
#  
#        @ingredients_text = node.text
#  
#        break
#  
#      end
#  
#      # found allergy advice flag it
#      get_this_node = true if node.text =~ /Allergy Advice:/
#  
#    }    
#    
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    # get_morrison_nutrition_info_per_100g
#    # add a check for as prepared and other dodges
#    table = @product_page.at('table')
#        
#    # add header titles
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    #puts "Category".ljust(CATEGORY_WIDTH)+"Value".ljust(VALUE_WIDTH)
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    
#    nutrients = {}
#
#    # find which column the per 100g/ml is    
#    #col_100 = get_table_100g_colum(table, 2)   - only tested w/ sainburies
#    
#    table.search('tr').each { |tr|
#      title_column    = tr.children[0].text.downcase
#      quantity_column = tr.children[1].text.downcase
#      
#      next if title_column =~ /typical/      # check here for 'as prepared'
#      next if title_column =~ /reference/
#      
#      if quantity_column =~ @symbol_to_regex[:energy]
#        
#        nutrients[:energy] = (($1.to_f) / ENERGY_TO_KCAL).to_i
#        
#      end
#  
#      @symbol_to_regex.each_pair { |sym, regex|
#                
#        if title_column =~ regex
#          
#          quantity_column =~ /(\d+\.*\d*)\s*g/
#  
#          nutrients[sym] = $1.to_f.round(1)
#          #puts "     SYM:#{sym.to_s} - #{regex.to_s} = qty:#{quantity_column} - $1 #{$1} <"
#          
#        end
#  
#      }
#      
#      #puts "#{tr.children[0].text}".ljust(CATEGORY_WIDTH)+"#{tr.children[1].text}".ljust(VALUE_WIDTH)    
#    }
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    
#    @nutrition_info = SimpleNutrientInfo.new  @nick_name, @product_name, @product_url, nutrients 
#    
#  end
#
#
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_fatsecret #@product_page
#    @supplier_name = 'FatSecret'
#    # aparently Mars bars don't have any sugar!? 60% sugar
#    # https://www.fatsecret.com/calories-nutrition/mars/mars-bar
#    
#    #nutritable = nutpanel
#    @product_name = @product_page.css("h1").text
#    puts "\n\nPRODUCT NAME: #{@product_name} <"
#    
#    @price_per_package = None
#    #puts "Price per unit:  #{@price_per_package}"
#    
#    @price_per_measure = None
#    #puts "Price per measure:  #{@price_per_measure}"
#    
#    #item_code_text = @product_page.search(".//p[@class='itemCode']").text.strip         #> "Item code: 1294231"
#    #@supplier_item_code = item_code_text.sub('Item code:','').strip
#    #puts "Item code:  #{@supplier_item_code}"
#    
#    #table = @product_page.at('table')
#    # div.nutpanel > table - ".//div[@class='nutpanel']/table"
#    
#    #table = @product_page.css(".//div[@class='nutpanel']/table")
#    table = @product_page.css("div[@class='nutpanel']/table")
#    
#    spceialised_symbol_to_regex    = {
#      :energy =>            /calories\s+(\d+)$/, # $1 = kcal integer
#      :fat =>               /total fat\s*?([\d\.]+)g/,
#      :saturates =>         /saturated fat\s*?([\d\.]+)g/,
#      :mono-unsaturates =>  /monounsaturated fat\s*?([\d\.]+)g/,
#      :poly-unsaturates =>  /polyunsaturated fat\s*?([\d\.]+)g/,
#      :carbohydrates =>     /total carbohydrate\s*?([\d\.]+)g/,
#      :sugars =>            /sugars\s*?([\d\.]+)g/,
#      :protein =>           /protein\s*?([\d\.]+)g/,
#      :fibre =>             /fibre\s*?([\d\.]+)g/,
#      :salt =>              /sodium\s*?([\d\.]+)mg/,         
#      :alcohol =>           /alchol/
#    }
#    
#    @symbol_to_regex.merge!(spceialised_symbol_to_regex)
#    
#    nutrients = {}
#
#    # find which column the per 100g/ml is    
#    #col_100 = get_table_100g_colum(table, 2)   - only tested w/ sainburies
#    
#    table.search('tr').each { |tr|
#      
#      row_text = tr.text.gsub("\t",'').gsub("\r\n",'')
#      
#      pp row_text
#  
#      @symbol_to_regex.each_pair { |sym, regex|
#        
#        if row_text.downcase =~ regex
#          
#          #puts "FOUND: #{sym} - #{row_text} q:#{$1}"
#          #pp row_text
#          
#          if sym.to_s == 'salt'
#            nutrients[sym] = (($1.to_f / 1000.0) * 2.58).round(1) # 100g salt is 38.758g sodium
#          else
#            nutrients[sym] = $1.to_f.round(1)
#          end
#          
#        end
#      
#      }
#    }
#        
#    @nutrition_info = SimpleNutrientInfo.new  @nick_name, @product_name, @product_url, nutrients 
#   
#  end
#  
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_tesco #@product_page
#    @supplier_name = 'Tesco'
#    
#    #itemDetails > h1
#    @product_name = @product_page.css("h1").text.strip
#    #@product_name = @product_page.search(".//h1[@class='product-details-tile__title']").text.strip
#    puts "\n\nPRODUCT NAME: #{@product_name} <"
#    
#    #
#    
#    @price_per_package = @product_page.search(".//div[@class='price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item']").text.split.pop.strip  #> "95p/unit"
#    puts "Price per unit:  #{@price_per_package}"
#
#    price_per_measure_5off = @product_page.search(".//div[@class='price-per-quantity-weight']").text.strip  #> "48p/100g"
#    # returns "£0.11/100ml£0.11/100ml£0.11/100ml£0.11/100ml£0.11/100ml" or similar
#    
#    #currency = @product_page.search(".//div[@class='price-per-quantity-weight']//span[@class='currency']").text.strip  #> "48p/100g"
#    #value = @product_page.search(".//div[@class='price-per-quantity-weight']//span[@class='value']").text.strip  #> "48p/100g"
#    #weight = @product_page.search(".//div[@class='price-per-quantity-weight']//span[@class='weight']").text.strip  #> "48p/100g"    
#    #@price_per_measure = "#{currency}#{value}#{weight}"
#    
#    # returns 5 copies in a strangly encoded format - claiming to be utf-8
#    # @price_per_measure = price_per_measure_5off[0..(price_per_measure_5off.length/5 - 1)] # "£0.11/100ml"
#    # recode = price_per_measure_5off.encode('iso-8859-1').encode('utf-8')    
#    # currency_byte = recode[0]
#
#    #or - getting rid of odd £ -     
#    @price_per_measure = price_per_measure_5off.gsub(price_per_measure_5off[0], ' ').split.pop # "0.11/100ml"
#    puts "Price per measure:  #{@price_per_measure}" # 2:#{price_per_measure_5off}"
#    
#    #https://www.tesco.com/groceries/en-GB/products/278994762 < pop
#    @supplier_item_code = @product_page.uri.to_s.split('/').pop
#    puts "Item code:  #{@supplier_item_code}"
#        
#    @product_url         = @product_page.uri.to_s
#
#    
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    # get_ingredients
#    
#    ingredient_search = @product_page.search(".//div[@id='ingredients']//p[@class='product-info-block__content']")
#    
#    if ingredient_search                                      # make sure not None
#      
#      @ingredients_text = ingredient_search.text
#    
#      text_to_process = @ingredients_text
#      
#      text_to_process.gsub!("\u00A0", " ")                    # replace non breaking space
#      
#      text_to_process.gsub!(".", "")                          # remove full stops
#      
#      @ingredients = text_to_process.split(',').collect{ |i| i.strip }  # collect into array
#           
#    end
#    
#    puts "Ingredients: #{@ingredients_text} \n<"
#    puts "Ingredient array: #{@ingredients} \n<"
#   
#    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#    # nutrition_info_per_100g
#
#    
#    table = @product_page.search(".//table[@class='product__info-table']")
#        
#    table.search('tr').each { |tr|
#      puts "#{tr.children[0].text}".ljust(CATEGORY_WIDTH)+"#{tr.children[1].text}".ljust(CATEGORY_WIDTH)+"#{tr.children[2].text}".ljust(VALUE_WIDTH)
#    }
#    
#    nutrients = {}
#    
#    
#    # find which column the per 100g/ml is    
#    col_100 = get_table_100g_colum(table, 2)  # - only tested w/ sainburies - test once w tesco! :?
#
#    
#    table.search('tr').each { |tr|
#      title_column    = tr.children[0].text.downcase                        # specialise from morrison
#      quantity_column = tr.children[col_100].text.downcase                        # specialise from morrison
#      
#      next if title_column =~ /per 100g/    # check here for 'as prepared'  # specialise from morrison
#      next if title_column =~ /servings/                                    # specialise from morrison
#      next if title_column =~ /reference/
#      next if title_column =~ /as sold/
#      
#      if quantity_column =~ @symbol_to_regex[:energy]
#        
#        nutrients[:energy] = (($1.to_f) / ENERGY_TO_KCAL).to_i
#        
#      end
#      
#      @symbol_to_regex.each_pair { |sym, regex|
#        
#        if title_column =~ regex
#          
#          quantity_column =~ /(\d+\.*\d*)\s*g/
#      
#          nutrients[sym] = $1.to_f.round(1)
#          
#        end
#  
#      }
#      
#      puts "#{title_column}".ljust(CATEGORY_WIDTH)+"#{quantity_column}".ljust(VALUE_WIDTH)
#    }
#    #(CATEGORY_WIDTH+VALUE_WIDTH).times{ print "-"} ; puts
#    
#    #pp nutrients
#    
#    @nutrition_info = SimpleNutrientInfo.new  @nick_name, @product_name, @product_url, nutrients 
#    
#    
#
#   
#  end
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_waitrose #@product_page    
#    @supplier_name = 'Waitrose'
#  end
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_coop #@product_page  
#    @supplier_name = 'Co-op'
#  end
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_asda #@product_page  
#    @supplier_name = 'Asda'
#    puts @supplier_name
#    
#    #itemDetails > h1
#    #@product_name = @product_page.css("h1").text.strip
#    @product_name = @product_page.search(".//h1[@class='prod-title']").text.strip
#    puts "\n\nPRODUCT NAME: #{@product_name} <"
#    
#    # doesn't pull page in the same WAY?
#    # @product_page = mech_agent.page.search(".//div[@class='pd-right-cont']")
#    # asda-product-search-api < google
#    #https://www.google.com/search?q=asda-product-search-api&oq=asda-product-search-api&aqs=chrome..69i57j69i60.540j0j7&sourceid=chrome&ie=UTF-8
#
#    
#    #pp @product_page
#    
#    
#    #@price_per_package   = 0.0
#    #@price_per_measure   = 0.0
#    #@supplier_item_code  = ''
#    #@product_url         = ''
#    #@supplier_name       = ''
#    #@nutrition_info      = None 
#    #@ingredients         = {}  
#    #@ingredients_text    = ''
#  end
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_ocado #@product_page
#    @supplier_name = 'Ocado'
#  end
#
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_booker #@product_page    
#    @supplier_name = 'Booker'
#  end
#
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def scrape_specialist #@product_page    
#    @supplier_name = 'Specialist'
#    raise "We have a specialist?"
#  end
#
#  
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  # top level get nutrient request
#  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  def get_product_info url
#    product_info = None
#    
#    mech_agent = Mechanize.new { |agent|
#      agent.log = Logger.new "/Users/simon/a_syllabus/lang/ruby/scripts/z_data/mechanize/mechanize.log"
#      agent.history.clear
#      agent.redirect_ok = true  
#      agent.follow_meta_refresh = true
#      agent.keep_alive = true
#      agent.open_timeout = 30
#      agent.read_timeout = 30  
#      # pp Mechanize::AGENT_ALIASES # show list of agents - no mac chrome!
#      agent.user_agent_alias = 'Mac Safari'
#    }
#    
#    mech_agent.get(url)     # get page
#    
#    @product_page = mech_agent.page
#    
#    pp @product_page
#    
#    supplier_regex = [  
#      /(sainsburys)/,
#      /(morrisons)/,
#      /(tesco)/,
#      /(waitrose)/,
#      /(coop)/,
#      /(asda)/,
#      /(ocado)/,
#      /(booker)/,
#      /(fatsecret)/
#    ]
#    
#    
#    match = None
#      
#    supplier_regex.each{ |regex|    
#      url =~ regex
#      
#      match = $1
#      
#      break if $1    
#    }
#  
#    
#    # SAVE page for inspection
#    local_copy_location = '/Users/simon/a_syllabus/lang/ruby/scripts/z_data/mechanize'
#    
#    retireved_page_name = "retievd_page_from_#{match}.html"
#    
#    File.open( File.join(local_copy_location,retireved_page_name ), 'w') { |file| file << @product_page.body }
#    # file automatically closed by block
#  
#    
#    case match
#      
#    when 'sainsburys'
#      product_info = scrape_sainsburys
#      
#    when 'morrisons'
#      product_info = scrape_morrisons
#      
#    when 'tesco'
#      product_info = scrape_tesco
#      
#    when 'waitrose'
#      product_info = scrape_waitrose
#      
#    when 'coop'
#      product_info = scrape_coop
#      
#    when 'asda'
#      product_info = scrape_asda
#      
#    when 'ocado'
#      product_info = scrape_ocado
#    
#    when 'booker'
#      product_info = scrape_booker
#    
#    when 'fatsecret'
#      product_info = scrape_fatsecret
#            
#    when None
#      product_info = scrape_specialist
#      
#    end
#      
#    product_info
#  end   
#   
#  # find which column the per 100g/ml is 
#  def get_table_100g_colum(table, default_col=2)        
#    col_100 = None
#    
#    #puts "> > > > > COL: #{col_100}"
#    #pp table.search('tr').first
#    table.search('tr').each{ |tr|
#      tr.children.each_with_index{ |c, index|
#        #puts "#{index} - #{c.text}"
#        if c.text =~ /per\s+100(g|ml)/i
#          col_100 = index
#          #puts "NEW col_100: #{col_100}"
#        end
#      }
#    }
#    col_100 = col_100 || default_col # default value 2
#    #puts "> > > > > COL: #{col_100}"    
#    #col_100
#  end
#   
#end
#
## Use get_product_info.rb for CLI access test urls etc         
