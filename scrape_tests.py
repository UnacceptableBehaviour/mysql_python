#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint

tests = {}
tests['https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755'] = { 'ri_name': 'wtr chicken thighs skin & bone',
  'igdt_type': 'atomic',
  'product_name': 'Essential Chicken Thighs, Skin-on & Bone-in',
  'price_per_package': '£3.60',
  'units': 'kg',
  'qty': 1.0,
  'no_of_each': 0,
  'package_in_g': 99999999,
  'alt_package_in_g': 1000.0,
  'package_qty_str': '1kg',
  'price_per_measure': '£3.60/kg',
  'multipack_qty': 1,
  'supplier_item_code': '',
  'product_url': 'https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755',
  'supplier_name': 'Waitrose',
  'nutrition_info': { 'energy': 238,
                      'fat': 15.2,
                      'saturates': 3.6,
                      'mono-unsaturates': 0.0,
                      'poly-unsaturates': 0.0,
                      'omega_3_oil': 0.0,
                      'carbohydrates': 0.4,
                      'sugars': 0.0,
                      'starch': 0.0,
                      'protein': 25.1,
                      'fibre': 0.0,
                      'salt': 0.19,
                      'alcohol': 0.0},
  'i_list': [],
  'i_text': '__igdts__',
  'allergens': set(),
  'allergens_raw': '',
  'product_desc': '',
  'product_page': None,
  'nutrinfo_text': '\n'
                   '\n'
                   '------------------ for the nutrition information wtr '
                   'chicken thighs skin & bone '
                   '(https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755)\n'
                   'energy              \t       238\n'
                   'fat                 \t      15.2\n'
                   'saturates           \t       3.6\n'
                   'mono-unsaturates    \t       0.0\n'
                   'poly-unsaturates    \t       0.0\n'
                   'omega_3_oil         \t       0.0\n'
                   'carbohydrates       \t       0.4\n'
                   'sugars              \t       0.0\n'
                   'starch              \t       0.0\n'
                   'protein             \t      25.1\n'
                   'fibre               \t       0.0\n'
                   'salt                \t      0.19\n'
                   'alcohol             \t       0.0\n'
                   '                                                Total '
                   '(100g)\n'
                   'ingredients: __igdts__\n'
                   'igdt_type: atomic'}



# # - - - - - - 
# urls_to_process_sbs = [ ('prune yogurt','https://www.tesco.com/groceries/en-GB/products/308111910'),
#                         ('kettle sea salt','https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g'),
#                         ('black turtle beans','https://www.tesco.com/groceries/en-GB/products/256530942'), # frist address
#                         ('cheese & garlic flat bread','https://www.tesco.com/groceries/en-GB/products/288610223'),
#                         ('tsc apple and raspberry juice','https://www.tesco.com/groceries/en-GB/products/278994762'),
#                         ('bacon frazzles','https://www.tesco.com/groceries/en-GB/products/260085541'),
#                         ('frazzles','https://www.tesco.com/groceries/en-GB/products/260085541'),
#                         ('kikkoman soy sauce','https://www.tesco.com/groceries/en-GB/products/281865197'),
#                         ('tsc soy sauce','https://www.tesco.com/groceries/en-GB/products/294781229'),
#                         ('veg oil','https://www.tesco.com/groceries/en-GB/products/254918073'),
#                         ('large medjool dates','https://www.tesco.com/groceries/en-GB/products/302676947'),                            
#                         ('tsc roquefort','https://www.tesco.com/groceries/en-GB/products/277465578'),   # has no ingredient but does have allergens
#                         ('anchovies','https://www.tesco.com/groceries/en-GB/products/310103367'),
#                         ('salted cashews','https://www.tesco.com/groceries/en-GB/products/297385240'),    # NO NUTRITION TABLE - USE AS test case fall back on 
#                         ('tsc smoked mackerel','https://www.tesco.com/groceries/en-GB/products/251631139'), # NUTRITION table has ug & mg in nutrition table
#                         ('beaujolais villages','https://www.tesco.com/groceries/en-GB/products/252285938'),
#                         ('tsc chicken roll','https://www.tesco.com/groceries/en-GB/products/299955420'),
#                         ('pork ribs','https://www.tesco.com/groceries/en-GB/products/281085768'),
#                         ('chicken stock cubes',''),
#                         ('fish fingers','https://www.tesco.com/groceries/en-GB/products/302861814'),   # * in ingredients                        
#                         ('niknaks', 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk'),
#                         ('hot cross buns','https://www.sainsburys.co.uk/gol-ui/product/sainsburys-fruity-hot-cross-buns--taste-the-difference-x4-280g'),
#                         ('haggis','https://www.sainsburys.co.uk/gol-ui/product/macsween-traditional-haggis-454g'), 
#                         ('crisps','https://www.sainsburys.co.uk/shop/gb/groceries/walkers-cheese---onion-crisps-6x25g'), 
#                         ('veg stock cube','https://www.sainsburys.co.uk/shop/gb/groceries/knorr-stock-cubes--vegetable-x8-80g'),
#                         ('actimel veg','https://www.sainsburys.co.uk/shop/gb/groceries/actimel-fruit-veg-cultured-shot-green-smoothie-6x100g-%28600g%29'),
#                         ('beef monster munch','https://www.sainsburys.co.uk/shop/gb/groceries/monster-munch-roast-beef-x6-25g'),
#                         ('wotsits','https://www.sainsburys.co.uk/shop/gb/groceries/walkers/walkers-wotsits-really-cheesy-crisp-snacks-36g'),                        
#                         ]
# urls_to_process_mrs = [ ('mrs butterscotch crunch','https://groceries.morrisons.com/webshop/product/Border-Sweet-Memories-Butterscotch-Crunch/483706011'), #NO EXIST
#                         ('mrs chicken korma','https://groceries.morrisons.com/webshop/product/Morrisons-Takeaway-Chicken-Korma/299170011'),      # ALLERGY processin i_string, Almond, Cashew nuts - MISS
#                         ('70% choc','https://groceries.morrisons.com/webshop/product/Lindt-Excellence-70-Cocoa-Dark-Chocolate/115160011'),
#                         ('clarified butter','https://groceries.morrisons.com/webshop/product/KTC-Pure-Butter-Ghee/233485011'),
#                         ('condensed milk','https://groceries.morrisons.com/webshop/product/Carnation-Cook-with-Condensed-Milk/110802011'),
#                         ('mature gouda','https://groceries.morrisons.com/products/landana-extra-mature-gouda-585420011'),                           
#                         ('diced chorizo','https://groceries.morrisons.com/products/morrisons-diced-spanish-chorizo-348095011'),
#                         ('chorizo','https://groceries.morrisons.com/products/elpozo-chorizo-ring-456221011'),
#                         ('clay oven garlic and coriander naan','https://groceries.morrisons.com/webshop/product/The-Clay-Oven-Bakery-Garlic--Coriander-Naan-Bread/336891011'),
#                         ('smoked mackerel fillet','https://groceries.morrisons.com/webshop/product/Morrisons-Smoked-Mackerel-Fillets/442534011'),
#                         ('beetroot brioche bun','https://groceries.morrisons.com/webshop/product/Morrisons-The-Best-Beetroot-Brioche-Rolls-/427428011'),
#                         ('mrs tikka masala sauce','https://groceries.morrisons.com/webshop/product/Morrisons-Tikka-Masala-Sauce/215269011'),
#                         ('spanish goats cheese','https://groceries.morrisons.com/webshop/product/Morrisons-Somerset-Goats-Cheese/111950011'),
#                         ('caramac buttons','https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac'),
#                         ('caramac','https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac'),
#                         ('cream cheese','https://groceries.morrisons.com/webshop/product/Philadelphia-Original-Soft-Cheese/251401011'),
#                         ('pistachios','https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011'),
#                         ('pistachio nuts','https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011'),
#                         ('crunchie bar','https://groceries.morrisons.com/webshop/product/Cadbury-Crunchie-Chocolate-Bar-4-Pack/269519011'),
#                         ('white bread','https://groceries.morrisons.com/webshop/product/Morrisons-White-Toastie-Loaf/217833011'),
#                         ('hoisin sauce','https://groceries.morrisons.com/webshop/product/Flying-Goose-Hoisin-Sauce/387755011'),
#                         ('giant mrs yorkshire pudding','https://groceries.morrisons.com/webshop/product/Morrisons-Giant-Yorkshire-Pudding/111374011'),
#                         ('mrs beef stock cube as prepared','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
#                         ('beef stock','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
#                         ('mrs beef stock cube','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
#                         ('wholegrain mustard','https://groceries.morrisons.com/webshop/product/Morrisons-Wholegrain-Mustard/121390011'),
#                         ('mrs veg samosa','https://groceries.morrisons.com/webshop/product/Morrisons-Indian-Takeaway-Vegetable-Samosas/114583011'),
#                         ]
# urls_to_process_asd = [ ('10% minced beef','https://groceries.asda.com/product/beef-mince-meatballs/asda-butchers-selection-beef-reduced-fat-mince/1000269713149'), # nutritional values @ asda are for pan fried mince!!
#                         ('asd mash potato','https://groceries.asda.com/product/prepared-roasting-veg/asda-smooth-buttery-classic-mash/38759'),
#                         ('asd honey nut cornflakes','https://groceries.asda.com/product/cornflakes-honey-nut/asda-corn-flakes/1000383159255'),
#                         ('asd xtra mash potato','https://groceries.asda.com/product/prepared-potatoes/asda-extra-special-creamy-mash/13852585'),
#                         ('white flatbread','https://groceries.asda.com/product/pitta-naan-bread-flatbread/asda-2-plain-naans/1000197472217'),
#                         ('smoked salmon trimmings','https://groceries.asda.com/product/smoked-salmon/asda-smoked-salmon-trimmings/910003094926'),        # only gets title on 3rd try??
#                         ('asd spring onions','https://groceries.asda.com/product/celery-spring-onions/asda-fragrant-crunchy-spring-onions/43994118'),
#                         ('leeks','https://groceries.asda.com/product/onions-leeks/asda-mild-sweet-trimmed-leeks/27003'),
#                         ('asd cooked red lentils','https://groceries.asda.com/product/dried-pulses-lentils-couscous/asda-dried-red-lentils/910001794651'),
#                         ('asd red lentils','https://groceries.asda.com/product/dried-pulses-lentils-couscous/asda-dried-red-lentils/910001794651'), # 30g = 80g cooked so uncooked x 80/30 x 80g numbers x 10/8 to per 100g # check for caveats: prepared as directed , pan fried, etc
#                         ('mayo','https://groceries.asda.com/product/mayonnaise/hellmanns-mayonnaise-real/910000246685'),
#                         ('asd mango chutney','https://groceries.asda.com/product/indian-takeaway/asda-indian-pickle-tray/910002615465'),
#                         ('asd garlic flatbread','https://groceries.asda.com/product/flatbreads-ciabatta/asda-garlic-herb-flatbread/910002092926'),  # TODO 'price_per_package': 'was  \n£1.70\n£1.00'
#                         ('limes','https://groceries.asda.com/product/lemons-limes-grapefruit/asda-zingy-zesty-limes/910002721111'), # NO nutrinfo # 'units': '?', SB 'ea' 4pk . . . 'product_name': 'ASDA Zingy & Zesty Limes 4pk','price_per_package': '£1.00','price_per_measure': '25.0p/each',
#                         ('aromat','https://groceries.asda.com/product/marinades-rubs/knorr-aromat-seasoning/450621'),                # TODO Issue with FULL stop at end - remove all after full stop - food_sets
#                         ('asd olive oil','https://groceries.asda.com/product/olive-oil/asda-olive-oil/1000219339167'), # TODO H - 100 ml of Oil weigh 92 grams,         ISSUE 1l
#                         ('asd extra virgin olive oil','https://groceries.asda.com/product/olive-oil/asda-extra-virgin-olive-oil/1000219339224'),
#                         ('cheese & onion kettle','https://groceries.asda.com/product/sharing-crisps/kettle-chips-mature-cheddar-red-onion-sharing-crisps/1000383133444'), # TODO 'price_per_package': was / now issue                           
#                         ('asd onion rings','https://groceries.asda.com/product/sharing-crisps/asda-onion-rings-sharing-snacks/910000826621'),
#                         ('thick choc bicuits','https://groceries.asda.com/product/luxury-biscuits-gifts/bahlsen-choco-leibniz-milk-chocolate-biscuits/910001769916'),    # TODO 'price_per_package': was / now issue  # TODO also Energy 2112 kj / < random '/'
#                         ('asd es mgt','https://groceries.asda.com/product/seeded-grains-bread/asda-extra-special-wholemeal-multigrain-sliced-loaf/1000123650133'),                            
#                         ] 
# urls_to_process_wtr = [ ('wtr breaded calamari','https://www.waitrose.com/ecom/products/waitrose-breaded-calamari/895037-689932-689933'),
#                         ('wtr sweet pickle herring','https://www.waitrose.com/ecom/products/elsinore-herring-in-sweet-spicy-marinade/023229-11289-11290'),
#                         ('wtr raw baguette','https://www.waitrose.com/ecom/products/essential-waitrose-bake-at-home-white-baguettes/886566-746625-746626'),                            
#                         ('wtr diced yellowfin tuna','https://www.waitrose.com/ecom/products/waitrose-diced-msc-yellowfin-tuna/728814-754521-754522'),
#                         ('duchy organic side of salmon','https://www.waitrose.com/ecom/products/duchy-organic-orkney-whole-salmon-fillet/851835-486775-486776'),
#                         ('wtr chicken thighs skin & bone','https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755'),
#                         ('wtr organic chicken thighs skin & bone','https://www.waitrose.com/ecom/products/duchy-organic-chicken-thighs-skin-on-bone-in/063388-32185-32186'),
#                         ('wtr battery chicken','https://www.waitrose.com/ecom/products/essential-large-whole-chicken/645021-507910-507911'),                            
#                         ('wtr baby rainbow carrots','https://www.waitrose.com/ecom/products/no1-baby-rainbow-carrots/636147-581352-581353'),
#                         ('wtr carrots','https://www.waitrose.com/ecom/products/essential-carrots/085125-43221-43222'),
#                         ('wtr unearthed jamon serano','https://www.waitrose.com/ecom/products/unearthed-spanish-serrano-ham/831503-347894-347895'), # TODO should show up as pork
#                         ('wtr parma ham','https://www.waitrose.com/ecom/products/waitrose-parma-ham-6-slices/525474-156519-156520'),
#                         ('organic bananas','https://www.waitrose.com/ecom/products/duchy-organic-fairtrade-bananas/088937-45726-45727'),    # TODO - units SB 'ea' qty SB 6 both missing
#                         ('wtr lrg cucumber','https://www.waitrose.com/ecom/products/essential-cucumber/086468-44158-44159'),
#                         ('wtr unwaxed limes','https://www.waitrose.com/ecom/products/cooks-ingredients-unwaxed-limes/011269-5598-5599'),
#                         ('wtr flapjack','https://www.waitrose.com/ecom/products/waitrose-mini-flapjack-bites/777243-110540-110541'),
#                         ('wtr shiraz cabernet red wine','https://www.waitrose.com/ecom/products/wolf-blass-red-label-shiraz-cabernet/868136-779851-779852'),
#                         ('biscoff icecream stick','https://www.waitrose.com/ecom/products/wolf-blass-red-label-shiraz-cabernet/868136-779851-779852'),
#                         ('wtr fr pork sausages','https://www.waitrose.com/ecom/products/no1-free-range-12-pork-sausages/824649-275729-275730'),
#                         ('duchy organic beef ribeye','https://www.waitrose.com/ecom/products/duchy-organic-british-beef-ribeye-steak/015596-7493-7494'),                            
#                         ('wtr fairtrade bananas','https://www.waitrose.com/ecom/products/essential-fairtrade-bananas/088903-45703-45704'),
#                         ]   
 
# # ocado selling m&s ?!?!?!?
# urls_to_process_ocd = [('m&s pork straws', 'https://www.ocado.com/products/m-s-british-pork-crackling-straws-515023011')]  
# urls_to_process_ald = [('smoked ham','https://groceries.aldi.co.uk/en-GB/p-cooked-smoked-ham-400g/5027951005828')] # horendous multiple products in single list: Cooked Ham Trimmings, Smoked Ham Trimmings, Peppered Ham Trimmings, Smoke Breaded Ham Trimmings & Honey Roasted Ham Trimmings Ingreadients back to back W/O punctuation!                    

# urls_to_process_all = { 'sbs': urls_to_process_sbs,
#                         'mrs': urls_to_process_mrs,
#                         'asd': urls_to_process_asd,
#                         'wtr': urls_to_process_wtr,
#                         'ocd': urls_to_process_ocd,
#                         'ald': urls_to_process_ald }

# # turn into dict
# urls_to_process_all_dict = {}
# for key,urls_to_process in urls_to_process_all.items():
#     # convert list tuple to dict
#     urls_to_process = {item[0]: item[1] for item in urls_to_process}
#     urls_to_process_all_dict[key] = urls_to_process

# pprint(urls_to_process_all_dict)
# print(f"urls_to_process_all_dict: {len(urls_to_process_all_dict)}")

urls_to_process_all_dict = {
'ald': {'smoked ham': 'https://groceries.aldi.co.uk/en-GB/p-cooked-smoked-ham-400g/5027951005828'},
'asd': {'10% minced beef': 'https://groceries.asda.com/product/beef-mince-meatballs/asda-butchers-selection-beef-reduced-fat-mince/1000269713149',
        'aromat': 'https://groceries.asda.com/product/marinades-rubs/knorr-aromat-seasoning/450621',
        'asd cooked red lentils': 'https://groceries.asda.com/product/dried-pulses-lentils-couscous/asda-dried-red-lentils/910001794651',
        'asd es mgt': 'https://groceries.asda.com/product/seeded-grains-bread/asda-extra-special-wholemeal-multigrain-sliced-loaf/1000123650133',
        'asd extra virgin olive oil': 'https://groceries.asda.com/product/olive-oil/asda-extra-virgin-olive-oil/1000219339224',
        'asd garlic flatbread': 'https://groceries.asda.com/product/flatbreads-ciabatta/asda-garlic-herb-flatbread/910002092926',
        'asd honey nut cornflakes': 'https://groceries.asda.com/product/cornflakes-honey-nut/asda-corn-flakes/1000383159255',
        'asd mango chutney': 'https://groceries.asda.com/product/indian-takeaway/asda-indian-pickle-tray/910002615465',
        'asd mash potato': 'https://groceries.asda.com/product/prepared-roasting-veg/asda-smooth-buttery-classic-mash/38759',
        'asd olive oil': 'https://groceries.asda.com/product/olive-oil/asda-olive-oil/1000219339167',
        'asd onion rings': 'https://groceries.asda.com/product/sharing-crisps/asda-onion-rings-sharing-snacks/910000826621',
        'asd red lentils': 'https://groceries.asda.com/product/dried-pulses-lentils-couscous/asda-dried-red-lentils/910001794651',
        'asd spring onions': 'https://groceries.asda.com/product/celery-spring-onions/asda-fragrant-crunchy-spring-onions/43994118',
        'asd xtra mash potato': 'https://groceries.asda.com/product/prepared-potatoes/asda-extra-special-creamy-mash/13852585',
        'cheese & onion kettle': 'https://groceries.asda.com/product/sharing-crisps/kettle-chips-mature-cheddar-red-onion-sharing-crisps/1000383133444',
        'leeks': 'https://groceries.asda.com/product/onions-leeks/asda-mild-sweet-trimmed-leeks/27003',
        'limes': 'https://groceries.asda.com/product/lemons-limes-grapefruit/asda-zingy-zesty-limes/910002721111',
        'mayo': 'https://groceries.asda.com/product/mayonnaise/hellmanns-mayonnaise-real/910000246685',
        'smoked salmon trimmings': 'https://groceries.asda.com/product/smoked-salmon/asda-smoked-salmon-trimmings/910003094926',
        'thick choc bicuits': 'https://groceries.asda.com/product/luxury-biscuits-gifts/bahlsen-choco-leibniz-milk-chocolate-biscuits/910001769916',
        'white flatbread': 'https://groceries.asda.com/product/pitta-naan-bread-flatbread/asda-2-plain-naans/1000197472217'},
'mrs': {'70% choc': 'https://groceries.morrisons.com/webshop/product/Lindt-Excellence-70-Cocoa-Dark-Chocolate/115160011',
        'beef stock': 'https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011',
        'beetroot brioche bun': 'https://groceries.morrisons.com/webshop/product/Morrisons-The-Best-Beetroot-Brioche-Rolls-/427428011',
        'caramac': 'https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac',
        'caramac buttons': 'https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac',
        'chorizo': 'https://groceries.morrisons.com/products/elpozo-chorizo-ring-456221011',
        'clarified butter': 'https://groceries.morrisons.com/webshop/product/KTC-Pure-Butter-Ghee/233485011',
        'clay oven garlic and coriander naan': 'https://groceries.morrisons.com/webshop/product/The-Clay-Oven-Bakery-Garlic--Coriander-Naan-Bread/336891011',
        'condensed milk': 'https://groceries.morrisons.com/webshop/product/Carnation-Cook-with-Condensed-Milk/110802011',
        'cream cheese': 'https://groceries.morrisons.com/webshop/product/Philadelphia-Original-Soft-Cheese/251401011',
        'crunchie bar': 'https://groceries.morrisons.com/webshop/product/Cadbury-Crunchie-Chocolate-Bar-4-Pack/269519011',
        'diced chorizo': 'https://groceries.morrisons.com/products/morrisons-diced-spanish-chorizo-348095011',
        'giant mrs yorkshire pudding': 'https://groceries.morrisons.com/webshop/product/Morrisons-Giant-Yorkshire-Pudding/111374011',
        'hoisin sauce': 'https://groceries.morrisons.com/webshop/product/Flying-Goose-Hoisin-Sauce/387755011',
        'mature gouda': 'https://groceries.morrisons.com/products/landana-extra-mature-gouda-585420011',
        'mrs beef stock cube': 'https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011',
        'mrs beef stock cube as prepared': 'https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011',
        'mrs butterscotch crunch': 'https://groceries.morrisons.com/webshop/product/Border-Sweet-Memories-Butterscotch-Crunch/483706011',
        'mrs chicken korma': 'https://groceries.morrisons.com/webshop/product/Morrisons-Takeaway-Chicken-Korma/299170011',
        'mrs tikka masala sauce': 'https://groceries.morrisons.com/webshop/product/Morrisons-Tikka-Masala-Sauce/215269011',
        'mrs veg samosa': 'https://groceries.morrisons.com/webshop/product/Morrisons-Indian-Takeaway-Vegetable-Samosas/114583011',
        'pistachio nuts': 'https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011',
        'pistachios': 'https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011',
        'smoked mackerel fillet': 'https://groceries.morrisons.com/webshop/product/Morrisons-Smoked-Mackerel-Fillets/442534011',
        'spanish goats cheese': 'https://groceries.morrisons.com/webshop/product/Morrisons-Somerset-Goats-Cheese/111950011',
        'white bread': 'https://groceries.morrisons.com/webshop/product/Morrisons-White-Toastie-Loaf/217833011',
        'wholegrain mustard': 'https://groceries.morrisons.com/webshop/product/Morrisons-Wholegrain-Mustard/121390011'},
'ocd': {'m&s pork straws': 'https://www.ocado.com/products/m-s-british-pork-crackling-straws-515023011'},
'sbs': {'actimel veg': 'https://www.sainsburys.co.uk/shop/gb/groceries/actimel-fruit-veg-cultured-shot-green-smoothie-6x100g-%28600g%29',
        'anchovies': 'https://www.tesco.com/groceries/en-GB/products/310103367',
        'bacon frazzles': 'https://www.tesco.com/groceries/en-GB/products/260085541',
        'beaujolais villages': 'https://www.tesco.com/groceries/en-GB/products/252285938',
        'beef monster munch': 'https://www.sainsburys.co.uk/shop/gb/groceries/monster-munch-roast-beef-x6-25g',
        'black turtle beans': 'https://www.tesco.com/groceries/en-GB/products/256530942',
        'cheese & garlic flat bread': 'https://www.tesco.com/groceries/en-GB/products/288610223',
        'chicken stock cubes': '',
        'crisps': 'https://www.sainsburys.co.uk/shop/gb/groceries/walkers-cheese---onion-crisps-6x25g',
        'fish fingers': 'https://www.tesco.com/groceries/en-GB/products/302861814',
        'frazzles': 'https://www.tesco.com/groceries/en-GB/products/260085541',
        'haggis': 'https://www.sainsburys.co.uk/gol-ui/product/macsween-traditional-haggis-454g',
        'hot cross buns': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-fruity-hot-cross-buns--taste-the-difference-x4-280g',
        'kettle sea salt': 'https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g',
        'kikkoman soy sauce': 'https://www.tesco.com/groceries/en-GB/products/281865197',
        'large medjool dates': 'https://www.tesco.com/groceries/en-GB/products/302676947',
        'niknaks': 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk',
        'pork ribs': 'https://www.tesco.com/groceries/en-GB/products/281085768',
        'prune yogurt': 'https://www.tesco.com/groceries/en-GB/products/308111910',
        'salted cashews': 'https://www.tesco.com/groceries/en-GB/products/297385240',
        'tsc apple and raspberry juice': 'https://www.tesco.com/groceries/en-GB/products/278994762',
        'tsc chicken roll': 'https://www.tesco.com/groceries/en-GB/products/299955420',
        'tsc roquefort': 'https://www.tesco.com/groceries/en-GB/products/277465578',
        'tsc smoked mackerel': 'https://www.tesco.com/groceries/en-GB/products/251631139',
        'tsc soy sauce': 'https://www.tesco.com/groceries/en-GB/products/294781229',
        'veg oil': 'https://www.tesco.com/groceries/en-GB/products/254918073',
        'veg stock cube': 'https://www.sainsburys.co.uk/shop/gb/groceries/knorr-stock-cubes--vegetable-x8-80g',
        'wotsits': 'https://www.sainsburys.co.uk/shop/gb/groceries/walkers/walkers-wotsits-really-cheesy-crisp-snacks-36g'},
'wtr': {'biscoff icecream stick': 'https://www.waitrose.com/ecom/products/wolf-blass-red-label-shiraz-cabernet/868136-779851-779852',
        'duchy organic beef ribeye': 'https://www.waitrose.com/ecom/products/duchy-organic-british-beef-ribeye-steak/015596-7493-7494',
        'duchy organic side of salmon': 'https://www.waitrose.com/ecom/products/duchy-organic-orkney-whole-salmon-fillet/851835-486775-486776',
        'organic bananas': 'https://www.waitrose.com/ecom/products/duchy-organic-fairtrade-bananas/088937-45726-45727',
        'wtr baby rainbow carrots': 'https://www.waitrose.com/ecom/products/no1-baby-rainbow-carrots/636147-581352-581353',
        'wtr battery chicken': 'https://www.waitrose.com/ecom/products/essential-large-whole-chicken/645021-507910-507911',
        'wtr breaded calamari': 'https://www.waitrose.com/ecom/products/waitrose-breaded-calamari/895037-689932-689933',
        'wtr carrots': 'https://www.waitrose.com/ecom/products/essential-carrots/085125-43221-43222',
        'wtr chicken thighs skin & bone': 'https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755',
        'wtr diced yellowfin tuna': 'https://www.waitrose.com/ecom/products/waitrose-diced-msc-yellowfin-tuna/728814-754521-754522',
        'wtr fairtrade bananas': 'https://www.waitrose.com/ecom/products/essential-fairtrade-bananas/088903-45703-45704',
        'wtr flapjack': 'https://www.waitrose.com/ecom/products/waitrose-mini-flapjack-bites/777243-110540-110541',
        'wtr fr pork sausages': 'https://www.waitrose.com/ecom/products/no1-free-range-12-pork-sausages/824649-275729-275730',
        'wtr lrg cucumber': 'https://www.waitrose.com/ecom/products/essential-cucumber/086468-44158-44159',
        'wtr organic chicken thighs skin & bone': 'https://www.waitrose.com/ecom/products/duchy-organic-chicken-thighs-skin-on-bone-in/063388-32185-32186',
        'wtr parma ham': 'https://www.waitrose.com/ecom/products/waitrose-parma-ham-6-slices/525474-156519-156520',
        'wtr raw baguette': 'https://www.waitrose.com/ecom/products/essential-waitrose-bake-at-home-white-baguettes/886566-746625-746626',
        'wtr shiraz cabernet red wine': 'https://www.waitrose.com/ecom/products/wolf-blass-red-label-shiraz-cabernet/868136-779851-779852',
        'wtr sweet pickle herring': 'https://www.waitrose.com/ecom/products/elsinore-herring-in-sweet-spicy-marinade/023229-11289-11290',
        'wtr unearthed jamon serano': 'https://www.waitrose.com/ecom/products/unearthed-spanish-serrano-ham/831503-347894-347895',
        'wtr unwaxed limes': 'https://www.waitrose.com/ecom/products/cooks-ingredients-unwaxed-limes/011269-5598-5599'}
}
#pprint(urls_to_process_all_dict)
print(f"urls_to_process_all_dict: {len(urls_to_process_all_dict)}")
