CREATE SCHEMA `receipe_cs50` ;

CREATE TABLE `recipe_cs50`.`recipes` (
  `rcp_id` INT NOT NULL,
  `image` VARCHAR(100) NULL,
  `title` VARCHAR(100) NOT NULL,
  `text_file` VARCHAR(100) NULL,
  `n_En` DECIMAL(2) NULL,
  `n_Fa` DECIMAL(2) NULL,
  `n_Ca` DECIMAL(2) NULL,
  `n_Su` DECIMAL(2) NULL,
  `n_Pr` DECIMAL(2) NULL,
  `n_Sa` DECIMAL(2) NULL,
  PRIMARY KEY (`rcp_id`),
  UNIQUE INDEX `rcp_id_UNIQUE` (`rcp_id` ASC));