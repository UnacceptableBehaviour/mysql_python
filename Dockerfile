FROM alpine

WORKDIR /

RUN apk update
RUN apk add nano git
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add --no-cache py3-pip

RUN python --version

#RUN git clone https://github.com/UnacceptableBehaviour/mysql_python

WORKDIR /mysql_python
COPY . .

#RUN python -m venv venv

RUN . venv/bin/activate

# move into requirements?
RUN pip3 install psycopg2

# strip this down to bare minimum
RUN pip install -r requirements.txt

EXPOSE 50015
ENTRYPOINT ["./hello.py"]

# build
# cd repos
# git clone https://github.com/UnacceptableBehaviour/mysql_python
# cd mysql_python
# docker build . -t dtk_health

# run with (network not quite right yet)
# docker run -e DATABASE_URL="postgresql://simon:@Simons-MBP:5432/cs50_recipes" \
# -e FLASK_ENV=development -e FLASK_APP=hello.py \
# --name dtk \
# --network=host \
# -p50015:50015 \
# --mount type=bind,source="/Users/simon/a_syllabus/lang/python/mysql_python/scratch/scratch",target=/mysql_python/scratch \
# --mount type=bind,source="/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/y949_tracker_archive",target=/mysql_python/scratch/archive \
# dtk_health
