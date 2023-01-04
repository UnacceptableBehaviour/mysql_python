FROM alpine

WORKDIR /mysql_python

RUN apt-get update
RUN apt-get install python

COPY . .

RUN pip install -r requirements.txt

COPY ../../lang/python/mysql_python/scratch/config_files.json ./scratch
COPY ../../lang/python/mysql_python/scratch/server.crt ./scratch
COPY ../../lang/python/mysql_python/scratch/server.key ./scratch 

# temp disperse into DBs
COPY ../../lang/python/mysql_python/scratch/___LAB_RECIPE_SMALLEST_DTK_TEST.txt
COPY ../../lang/python/mysql_python/scratch/z_product_nutrition_info_autogen_DTK_cal.txt
COPY ../../lang/python/mysql_python/scratch/z_usersDTK_DB.json
COPY ../../lang/python/mysql_python/scratch/z_users_DB.json
COPY ../../lang/python/mysql_python/scratch/z_users_devices_DB.json

COPY /Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt ./scratch/nutrinfo.txt



# set app env var
# FLASK_ENV=development
# FLASK_APP=hello.py
#ENTRYPOINT ["FLASK_APP=/mysql_python/hello.py","FLASK_ENV=development","./hello.py"]

EXPOSE 50015
ENTRYPOINT ["./hello.py"]

# cd /Users/simon/a_syllabus/lang/python/mysql_python
# docker run -d --name dtk_health --rm --mount type=bind,source="$(pwd)",target=/mysql_python -p50015:50015 dtk_health
# docker build --name=dtk_health -t dtk_python

# cd /Users/simon/a_syllabus/repos
# git clone https://github.com/UnacceptableBehaviour/mysql_python
# cd mysql_python
# docker build . -t dtk_health

# docker run -d -e FLASK_ENV=development -e FLASK_APP=hello.py --name dtk -p50015:50015 --mount type=bind,source="/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/y949_tracker_archive",target=/mysql_python/scratch/archive dtk_health
