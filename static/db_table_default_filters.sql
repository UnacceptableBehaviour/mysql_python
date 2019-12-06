CREATE TABLE IF NOT EXISTS default_filters (
  uuid_user VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
  allergens VARCHAR(50) ARRAY,
  ingredient_exc VARCHAR(50) ARRAY,
  tags_exc VARCHAR(50) ARRAY,
  tags_inc VARCHAR(50) ARRAY,
  type_exc VARCHAR(50) ARRAY,
  type_inc VARCHAR(50) ARRAY
);
