CREATE TABLE IF NOT EXISTS fav_rcp_ids (
  uuid_user VARCHAR(100),
  fav_rcp_id INT,
  PRIMARY KEY (uuid_user, fav_rcp_id) 
);