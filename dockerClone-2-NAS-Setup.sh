#!/usr/bin/env zsh

# before cloning - FIX so uses env var!!!!
# in helpers_db.py
# set db_to_use = 'POSTGRES_DB_DOCKER_INTERNAL_NAS'
# push to git

# Make sure NAS mounted
# cd /Volumes/docker/dtk-swarm-2/dtk_health
# git clone https://github.com/UnacceptableBehaviour/mysql_python
# cd mysql_python
# chmod +x dockerClone-2-NAS-Setup.sh
# ./dockerClone-2-NAS-Setup.sh

# copy 'unmanaged' private config files over - from original repo
# config files, ruby scripts
mkdir scratch
mkdir scratch/_docr_support
mkdir scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/nutrinfo.txt ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/___LAB_RECIPE_SMALLEST_DTK_TEST.txt ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_product_nutrition_info_autogen_DTK_cal.txt ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_usersDTK_DB.json ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_users_DB.json ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_users_devices_DB.json ./scratch/_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/config_files.json ./scratch/_docr_support

# Define the source and target directories
src="/Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/archive/014752da-b49d-4fb0-9f50-23bc90e44298_carter_1703566856299_2023 12 26.json"
target="./scratch/_docr_support/archive"

# Create the target directory if it doesn't exist
mkdir -p "$target"

# Copy the file
cp "$src" "$target"


cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.crt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.key ./scratch

# cp RUBY SCRIPTS OVER
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/ccm_nutridoc_web.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_data_structures.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_debug.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_file_services.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_tools.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/recipe.rb ./scratch/_ruby_scripts

# that gets things ready for container manager to build dtk container
