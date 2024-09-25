CREATE TABLE IF NOT EXISTS usernames (
  uuid_user VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  update_time_stamp BIGINT
);