CREATE TABLE IF NOT EXISTS recipes (
  id BIGSERIAL PRIMARY KEY,
  ri_id BIGINT NOT NULL UNIQUE,

  ri_name VARCHAR(100) NOT NULL,
  yield DECIMAL(9,2) DEFAULT NULL,
  units VARCHAR(10) DEFAULT NULL,
  servings DECIMAL(9,2) DEFAULT NULL,
  density DECIMAL(9,2) DEFAULT NULL,
  serving_size DECIMAL(9,2) DEFAULT NULL,
  atomic  BOOLEAN DEFAULT FALSE,
  
  ingredients     VARCHAR(150) ARRAY,
  allergens       VARCHAR(150) ARRAY,
  tags            VARCHAR(150) ARRAY,
  user_tags       VARCHAR(150) ARRAY,
  type            VARCHAR(150) ARRAY,

  lead_image VARCHAR(100) DEFAULT NULL,
  text_file VARCHAR(100) DEFAULT NULL,
  description VARCHAR(500) DEFAULT NULL,
  images VARCHAR(2000) DEFAULT NULL,
  method VARCHAR(2000) DEFAULT NULL,
  notes VARCHAR(2000) DEFAULT NULL,
  user_rating DECIMAL(9,2) DEFAULT NULL,
  username VARCHAR(50) DEFAULT NULL,

  n_En DECIMAL(9,2) DEFAULT NULL,
  n_Fa DECIMAL(9,2) DEFAULT NULL,
  n_Fs DECIMAL(9,2) DEFAULT NULL,
  n_Fm DECIMAL(9,2) DEFAULT NULL,
  n_Fp DECIMAL(9,2) DEFAULT NULL,
  n_Fo3 DECIMAL(9,2) DEFAULT NULL,
  n_Ca DECIMAL(9,2) DEFAULT NULL,
  n_Su DECIMAL(9,2) DEFAULT NULL,
  n_Fb DECIMAL(9,2) DEFAULT NULL,
  n_St DECIMAL(9,2) DEFAULT NULL,
  n_Pr DECIMAL(9,2) DEFAULT NULL,
  n_Sa DECIMAL(9,2) DEFAULT NULL,
  n_Al DECIMAL(9,2) DEFAULT NULL
);