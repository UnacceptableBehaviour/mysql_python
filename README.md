# mysql_python
hook python upto mysql db

** Connect to  DB **

```
$ export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/11/bin

$ psql

# \c cs50_recipes           # connect to DB. No ; needed is psql command

# \d recipes                # descirbe table - show column names & data types

# SELECT ri_name, tags, allergens FROM recipes;         # SQL query
```


** Rebuild DB **
```
asset_server$ http-server -p 8000 --cors        # fire up asset server

$ populate_db.py                                # rebuild the DB from assest server
```

** Note to force an asset server rebuild before rebuilding DB uncomment line: **
```
force_complete_rebuid = True            # set flag true
executes:
population_data = subprocess.check_output(['populate_asset_server.rb'])
                                        # and deletes tables in DB
```
For example after wrangling assets or inclusion of new assets etc . . .
