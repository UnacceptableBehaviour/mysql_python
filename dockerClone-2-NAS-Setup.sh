#!/usr/bin/env zsh

# Make sure NAS mounted
# place this file in /Volumes/docker/dtk-swarm-2
# run it to upgdate the mysql_python repo

cd /Volumes/docker/dtk-swarm-2/dtk_health/

# remove the old repo
rm -rf mysql_python

# clone new one in place
git clone https://github.com/UnacceptableBehaviour/mysql_python

cd mysql_python
# chmod +x dockerClone-2-NAS-Setup.sh

# update the docker-compose.yml in Project on NAS from docker-compose-NAS.yml IF NEEDED

# copy 'unmanaged' private config files over - from original repo
# config files, ruby scripts
mkdir scratch
mkdir scratch/_ruby_scripts
#mkdir scratch/_docr_support    # automatically created in container when mounted

# cp RUBY SCRIPTS OVER
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/ccm_nutridoc_web.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_data_structures.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_debug.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_file_services.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/foodlab_tools.rb ./scratch/_ruby_scripts
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_ruby_scripts/recipe.rb ./scratch/_ruby_scripts

# deprecated - REMOVE - Reverse proxy now does the SSL stuff
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.crt ./scratch
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/server.key ./scratch

# want _docr_support to persist across rebuilds - so map it to a volume in compose file
cd ..
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/nutrinfo.txt ./_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/___LAB_RECIPE_SMALLEST_DTK_TEST.txt ./_docr_support
# z_usersDTK_DB.json contains diary entries so don't overwrite it if it exists!
# diary will persist across rebuilds
if [ ! -f ./_docr_support/z_usersDTK_DB.json ]; then
    cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_usersDTK_DB.json ./_docr_support
fi
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_users_DB.json ./_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/z_users_devices_DB.json ./_docr_support
cp /Users/simon/a_syllabus/lang/python/mysql_python/scratch/_docr_support/config_files.json ./_docr_support

# This is now stored off container at: /Volumes/docker/dtk-swarm-2/dtk_health/archive
# and tha is mapped in the container to
# mysql_python/scratch/_docr_support/archive
# diary entries are retained in the archive when the conatiner is rebuilt


# that gets things ready for container manager to build dtk container

