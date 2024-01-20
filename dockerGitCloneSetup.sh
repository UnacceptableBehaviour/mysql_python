#!/usr/bin/env zsh

# cd /a_syllabus/repos
# then run me

git clone https://github.com/UnacceptableBehaviour/mysql_python

cd mysql_python
python -m venv venv
. venv/bin/activate                    # .pe
pip install -r requirements.txt

# copy 'unmanaged' private config files over - from original repo
# config files, SSL certs etc 
mkdir scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/nutrinfo.txt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/___LAB_RECIPE_SMALLEST_DTK_TEST.txt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/z_product_nutrition_info_autogen_DTK_cal.txt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/z_usersDTK_DB.json ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/z_users_DB.json ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/z_users_devices_DB.json ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/config_files.json ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.crt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.key ./scratch

docker build . -t dtk_health
