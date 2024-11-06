#! /usr/bin/env python

# indexes for ingredients row
ATOMIC_INDEX = 0                    # default value is 1 - TRUE
QTY_IN_G_INDEX = 1
SERVING_INDEX = 2
INGREDIENT_INDEX = 3
TRACK_NIX_TIME = 4
IMAGE_INDEX = 5
HTML_ID = 6


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def ingredient_in_recipe_list(ingredient, recipies_and_subcomponents):
#     found = None
#
#     for recipe in recipies_and_subcomponents:
#         if recipe['ri_name'] == ingredient[INGREDIENT_INDEX]:
#             found = recipe
#
#     return found

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# typical recipe
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#{'ingredients': [[0, '250g', '(0)', 'cauliflower', nix_time_in_ms],    # sublist
#                 [0, '125g', '(0)', 'grapes', nix_time_in_ms],
#                 [0, '200g', '(4)', 'tangerines', nix_time_in_ms],
#                 [0, '55g', '(0)', 'dates', nix_time_in_ms],
#   atomic >-------0, '8g', '(0)', 'coriander', nix_time_in_ms],
#                 [0, '8g', '(0)', 'mint', nix_time_in_ms],
#                 [0, '4g', '(0)', 'chillies', nix_time_in_ms],
#   sub_comp >-----1, '45g', '(0)', 'pear and vanilla reduction lite', nix_time_in_ms],
#                 [0, '2g', '(0)', 'salt', nix_time_in_ms],
#                 [0, '2g', '(0)', 'black pepper', nix_time_in_ms],
#                 [0, '30g', '(0)', 'flaked almonds', nix_time_in_ms]],
#  'ri_name': 'cauliflower california',
#  'atomic' : 0     ** deprecated BOOL use igdt_type INT8 instead
#  'igdt_type' : -1 to 3  see below
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# //  IGDT_TYPE: UNCHECKED / ATOMIC / DERIVED / OTS / DTK
# //                 -1         0        1       2     3
# add IGD_TYPE_NO_INFO   = -2;   
# let IGD_TYPE_UNCHECKED = -1;
# let IGD_TYPE_ATOMIC    = 0;
# let IGD_TYPE_DERIVED   = 1;
# let IGD_TYPE_OTS       = 2;   // Off The Shelf
# let IGD_TYPE_DTK       = 3;   // Daily TracKer 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# cs50_recipes=# \d recipes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                         Table "public.recipes"
#     Column    |           Type           | Collation | Nullable |               Default
# --------------+--------------------------+-----------+----------+-------------------------------------
#  id           | bigint                   |           | not null | nextval('recipes_id_seq'::regclass)
#  ri_id        | bigint                   |           | not null |
#  ri_name      | character varying(100)   |           | not null |
#  yield        | numeric(9,2)             |           |          | NULL::numeric
#  units        | character varying(10)    |           |          | NULL::character varying
#  servings     | numeric(9,2)             |           |          | NULL::numeric
#  density      | numeric(9,2)             |           |          | NULL::numeric
#  serving_size | numeric(9,2)             |           |          | NULL::numeric
#  ingredients  | character varying(150)[] |           |          |
#  allergens    | character varying(150)[] |           |          |
#  tags         | character varying(150)[] |           |          |
#  user_tags    | character varying(150)[] |           |          |
#  lead_image   | character varying(100)   |           |          | NULL::character varying
#  text_file    | character varying(100)   |           |          | NULL::character varying
#  n_en         | numeric(9,2)             |           |          | NULL::numeric
#  n_fa         | numeric(9,2)             |           |          | NULL::numeric
#  n_fs         | numeric(9,2)             |           |          | NULL::numeric
#  n_fm         | numeric(9,2)             |           |          | NULL::numeric
#  n_fp         | numeric(9,2)             |           |          | NULL::numeric
#  n_fo3        | numeric(9,2)             |           |          | NULL::numeric
#  n_ca         | numeric(9,2)             |           |          | NULL::numeric
#  n_su         | numeric(9,2)             |           |          | NULL::numeric
#  n_fb         | numeric(9,2)             |           |          | NULL::numeric
#  n_st         | numeric(9,2)             |           |          | NULL::numeric
#  n_pr         | numeric(9,2)             |           |          | NULL::numeric
#  n_sa         | numeric(9,2)             |           |          | NULL::numeric
#  n_al         | numeric(9,2)             |           |          | NULL::numeric
# Indexes:
#     "recipes_pkey" PRIMARY KEY, btree (id)
#     "recipes_ri_id_key" UNIQUE CONSTRAINT, btree (ri_id)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# all fields
# ['id','ri_id','ri_name','yield','units','servings','density','serving_size','igdt_type','ingredients','allergens','tags',
# 'user_tags','lead_image','text_file','n_en','n_fa','n_fs','n_fm','n_fp','n_fo3','n_ca','n_su','n_fb','n_st','n_pr','n_sa','n_al',]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def return_recipe_dictionary():
#     nix_time_in_ms = nix_time_ms()

#     return {
#         # fields super sections
#         # header:       name image desc             EG gallery
#         'ri_id': 0,
#         'ri_name':'none_listed',
#         'lead_image':'none_listed',
#         'text_file':'none_listed',
#         'description': 'add a description . . .',
#         'igdt_type': -1,
#         'user_rating': 1,
#         'dt_date': nix_time_in_ms,
#         'dt_date_readable': hr_readable_date_from_nix(nix_time_in_ms),
#         'dt_day': day_from_nix_time(nix_time_in_ms),
#         'dt_time': time24h_from_nix_time(nix_time_in_ms),
#         'dt_rollover': roll_over_from_nix_time(nix_time_in_ms),
#         'dt_last_update': 0,
#         'username':'carter',

#         # info:         nurients, servings, etc     Traffic Lights & Nutrition
#         'nutrinfo': {
#             'servings': 0,
#             'serving_size': 0,
#             'yield': '0g',
#             'units': 'g',
#             'density': 1,
#             'n_En':0, 'n_Fa':0, 'n_Fs':0, 'n_Fm':0, 'n_Fp':0, 'n_Fo3':0, 'n_Ca':0,
#             'n_Su':0, 'n_Fb':0, 'n_St':0, 'n_Pr':0, 'n_Sa':0, 'n_Al':0
#         },

#         # top level ingredients - look for sub component flags to dig deeper
#         'ingredients': [],
#         'method': {},

#         # tags:         tags, allergens, user_tags  Simplify classification
#         'allergens': [ 'none_listed' ],
#         'tags': [ 'none_listed' ],
#         'user_tags': [ 'none_listed' ],
#         'types': [ 'none_listed' ],

#         # SUB COMPONENT RECIPES
#         # components:  { 'component name': recipe dictionary, . . . }
#         'components': {},

#     }
