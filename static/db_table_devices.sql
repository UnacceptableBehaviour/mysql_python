CREATE TABLE IF NOT EXISTS devices (
  uuid_dev VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
  uuid_user VARCHAR(100) NOT NULL,
  platform VARCHAR(80),
  viewport VARCHAR(80),
  ua_os VARCHAR(80),
  ua_browser VARCHAR(80),
  last_com VARCHAR(80),
  last_loc VARCHAR(80)
);