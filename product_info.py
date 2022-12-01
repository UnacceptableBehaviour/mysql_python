#! /usr/bin/env python

import re
#import sys
#import itertools
from pprint import pprint
#from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# for expected conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
    asd_cookie_barrier = True
    ocd_cookie_barrier = True
    bkr_cookie_barrier = True

                
    def __init__(self, name, url):
        self.ri_name            = name  # nick_name
        self.product_name       = ''
        self.price_per_package  = 0.0
        self.package_in_g       = 0.0
        self.price_per_measure  = 0.0
        self.supplier_item_code = ''
        self.product_url        = url
        self.supplier_name      = ''
        self.nutrition_info     = None 
        self.i_list             = []    # ingredient list
        self.i_text             = ''    # ingredient raw text as scraped
    
        self.symbol_to_regex    = {
            'energy':            r'(\d+)\s*kj',    # $1 = kcal integer - kJ downcase kj
            'fat':               r'fat',
            'saturates':         r'\bsaturates\b',
            'mono_unsaturates':  r'mono',
            'poly_unsaturates':  r'poly',
            'omega_3':           r'omega',
            'carbohydrates':     r'carbohydrate',
            'sugars':            r'sugars',
            'starch':            r'starch',
            'protein':           r'protein',
            'fibre':             r'fibre',
            'salt':              r'salt',
            'alcohol':           r'alcohol'
        }
        
        self.product_page       = None   
        
        self.get_product_info()

    def __str__(self):
        return str(pprint(vars(self)))

    def scrape_sainsburys(self):        
        print(f"scraping SAINSBURIES: {self.product_url}")

        if ProductInfo.sbs_driver == None:
            ProductInfo.sbs_driver = webdriver.Chrome('chromedriver')        
        driver = ProductInfo.sbs_driver

        delay_in_seconds = 3    
        driver.get(self.product_url)

        allow_cookies_btn_id = 'onetrust-accept-btn-handler'
        if ProductInfo.sbs_cookie_barrier:
            try:
                print('try cookie_button w WAIT')
                cookie_button = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.ID, allow_cookies_btn_id)))
                print('cookie_button')
            except TimeoutException:
                print("Loading took too much time!")
            except Exception as exp:
                print(exp)
                print('cookie_button NOT FOUND')
            
            try:
                print('cookie_button CLICK')
                cookie_button.send_keys(Keys.RETURN)
                ProductInfo.sbs_cookie_barrier = False            
            except Exception as exp:
                print(exp)
                print('cookie_button NOT clicked')

        try:    # wait content load
            css_selector = 'h3.productDataItemHeader, h3.itemHeader'
            print(f'# # #> waiting for h3 tags: {css_selector}')
            h3_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            print(f'# # #> found for h3 tags:\n{h3_tags}')
        except TimeoutException:
            print("Waiting for INGREDIENTS took too much time!")
        except Exception as exp:
            print(exp)
            print('Ingredients NOT FOUND')
            
        # self.product_name       = ''
        # <h1 class="pd__header" data-test-id="pd-product-title">Nik Naks Nice'N'Spicy Grab Bag Crisps 45g</h1>
        # data-test-id="pd-product-title"
        try:
            #css_selector = 'h1[data-test-id="pd-product-title"]'
            css_selector = 'h1.pd__header[data-test-id="pd-product-title"]'
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.product_name = e.text.strip()
        except Exception as exp:
            print(exp)
            print('self.product_name NOT found!')        
        
        # self.price_per_package  = 0.0
        # <div aria-label="£1.80 was £2.40">£1.80</div
        # <div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined"><div aria-hidden="true"><span data-test-id="offer-original-price" class="pd__cost__original" aria-label="original price">£2.40</span></div><div aria-label="£1.80 was £2.40">£1.80</div></div>
        # <div aria-label="65p was undefined">65p</div>
        # <div data-test-id="pd-retail-price" class="pd__cost__total undefined"><div aria-label="65p was undefined">65p</div></div>
        #                       ^
        try:
            css_selector = 'div[data-test-id="pd-retail-price"]'
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.price_per_package = e.text.strip()
            self.package_in_g = 9999
        except Exception as exp:
            print(exp)
            print('self.price_per_package NOT found!')
            
        # self.price_per_measure  = 0.0
        # <div data-test-id="pd-unit-price" class="pd__cost__per-unit" aria-label="unit price and measure on offer">£12.00 / kg</div>
        # <div data-test-id="pd-unit-price" class="pd__cost__per-unit" aria-label="unit price and measure on offer">£2.11 / 100g</div>
        #                       ^
        try:
            css_selector = '[data-test-id="pd-unit-price"]'
            e = driver.find_element(By.CSS_SELECTOR, css_selector)
            self.price_per_measure = e.text.strip()
        except Exception as exp:
            print(exp)
            print('self.price_per_measure NOT found!')
            
        # self.supplier_item_code = ''
        # not for this supplier
                
        self.supplier_name      = 'Sainburys'
        # self.nutrition_info     = None
        
        # self.i_list             = []    # ingredient list
        # self.i_text             = ''    # ingredient raw text as scraped    
    
                
        try:
            css_selector = 'h3, .productDataItemHeader, .productIngredients, .productText'
            print(f'# # #> getting list of element w selector: {css_selector}')
            elist = driver.find_elements(By.CSS_SELECTOR, css_selector)
            f_igdt = False
            f_desc = False
            for e in elist:                
                print(f"> > > - - - : {e.text}")
                if f_igdt == True:
                    f_igdt = False
                    self.i_list = e.text.strip()
                    print(f">>IGDTs:{self.i_list}")                    
                if f_desc == True:
                    f_desc = False
                    self.product_name = e.text.strip()
                    print(f">>Item:{self.product_name}")
                if e.text.strip() == 'Ingredients':
                    f_igdt = True
                if e.text.strip() == 'Description':
                    f_desc = True
        except Exception as exp:
            print(exp)
            print('NOTHING!')
        

    def scrape_morrisons(self):
        print(f"scraping MORRISONS: {self.product_url}")        
        
    def scrape_tesco(self):
        print(f"scraping TESCO: {self.product_url}")
        driver = webdriver.Chrome('chromedriver')        
        delay_in_seconds = 3    
        driver.get(self.product_url)

    def scrape_waitrose(self):
        print(f"scraping WAITROSE: {self.product_url}")      
      
    def scrape_coop(self):
        print(f"scraping COOP: {self.product_url}")
      
    def scrape_asda(self):
        print(f"scraping ASDA: {self.product_url}")
      
    def scrape_ocado(self):
        print(f"scraping OCADO: {self.product_url}")
      
    def scrape_booker(self):
        print(f"scraping BOOKER: {self.product_url}")
      
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
          r'(booker)'       # bkr
        ]
        
        match = None
        for r in supplier_regex:
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
        
        elif match == None:
            self.scrape_specialist()

     
    # find which column the per 100g/ml is 
    def get_table_100g_colum(table, default_col=2):
        col_100 = None
        
        # table.search('tr').each{ |tr|
        #     tr.children.each_with_index{ |c, index|
        #         if c.text =~ /per\s+100(g|ml)/i
        #             col_100 = index
        # 
        #     }
        # }
        # col_100 = col_100 || default_col  
    



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
#      :mono_unsaturates =>  /monounsaturated fat\s*?([\d\.]+)g/,
#      :poly_unsaturates =>  /polyunsaturated fat\s*?([\d\.]+)g/,
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
