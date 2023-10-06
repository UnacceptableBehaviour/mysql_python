CREATE TABLE IF NOT EXISTS fav_rcp_ids (
  uuid_user VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
  fav_rcp_ids INT[]
);