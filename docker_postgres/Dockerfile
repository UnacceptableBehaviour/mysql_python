FROM postgres:13

EXPOSE 5432

ENV POSTGRES_USER simon
ENV POSTGRES_PASSWORD pool

VOLUME /var/lib/postgresql/data

CMD ["postgres"]


# build with
# cd /Users/simon/a_syllabus/lang/python/mysql_python/docker_postgres
# docker build -t postgres-rcp:13-custom .

# run with
# docker run -p 5432:5432 postgres-rcp:13-custom
#
# for persistent data
# docker run -d \
# -v /Users/simon/a_syllabus/lang/docker/postgres_data:/var/lib/postgresql/data \
# -p 5432:5432 \
# --name postgres-persistant \
# postgres-rcp:13-custom