

-- 1) тип кровельных материалов:

CREATE TABLE `roofing_materials`.`type_of_roofing_material` (
  `id_type_of_roofing_material` INT NOT NULL AUTO_INCREMENT,
  `name_type_of_roofing_material` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_type_of_roofing_material`),
  UNIQUE INDEX `id_type_of_roofing_material_UNIQUE` (`id_type_of_roofing_material` ASC) VISIBLE,
  UNIQUE INDEX `name_type_of_roofing_material_UNIQUE` (`name_type_of_roofing_material` ASC) VISIBLE);


INSERT INTO `roofing_materials`.`type_of_roofing_material` (`name_type_of_roofing_material`) VALUES ('Резино-полимерная кровля');
INSERT INTO `roofing_materials`.`type_of_roofing_material` (`name_type_of_roofing_material`) VALUES ('Металлочерепица');
INSERT INTO `roofing_materials`.`type_of_roofing_material` (`name_type_of_roofing_material`) VALUES ('Фальцевая кровля');



-- 2) цвет:

CREATE TABLE `color` (
  `id_color` int NOT NULL AUTO_INCREMENT,
  `name_color` varchar(45) NOT NULL,
  PRIMARY KEY (`id_color`),
  UNIQUE KEY `id_color_UNIQUE` (`id_color`),
  UNIQUE KEY `name_color_UNIQUE` (`name_color`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('зеленый');
INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('черный');
INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('коричневый');
INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('синий');
INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('красный');
INSERT INTO `roofing_materials`.`color` (`name_color`) VALUES ('серый');


-- 3) покрытие:

CREATE TABLE `coverage` (
  `id_coverage` int NOT NULL AUTO_INCREMENT,
  `name_coverage` varchar(45) NOT NULL,
  PRIMARY KEY (`id_coverage`),
  UNIQUE KEY `id_coverage_UNIQUE` (`id_coverage`),
  UNIQUE KEY `name_coverage_UNIQUE` (`name_coverage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `roofing_materials`.`coverage` (`name_coverage`) VALUES ('Gumibo');
INSERT INTO `roofing_materials`.`coverage` (`name_coverage`) VALUES ('NormanMP');
INSERT INTO `roofing_materials`.`coverage` (`name_coverage`) VALUES ('PURMAN');



-- 4) производитель/коллекция:

CREATE TABLE `brand` (
  `id_brand` int NOT NULL AUTO_INCREMENT,
  `name_brand` varchar(45) NOT NULL,
  PRIMARY KEY (`id_brand`),
  UNIQUE KEY `id_brand_UNIQUE` (`id_brand`),
  UNIQUE KEY `name_brand_UNIQUE` (`name_brand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `roofing_materials`.`brand` (`name_brand`) VALUES ('Barcelona');
INSERT INTO `roofing_materials`.`brand` (`name_brand`) VALUES ('Palermo');
INSERT INTO `roofing_materials`.`brand` (`name_brand`) VALUES ('Roman');



-- 5) материалы:

CREATE TABLE `materials` (
  `id_materials` int NOT NULL AUTO_INCREMENT,
  `name_materials` varchar(100) NOT NULL,
  `thickness` float NOT NULL,
  `place` float NOT NULL,
  `count` int NOT NULL,
  `price` float NOT NULL,
  `id_type_of_roofing_material` int NOT NULL,
  `id_color` int NOT NULL,
  `id_coverage` int NOT NULL,
  `id_brand` int NOT NULL,
  PRIMARY KEY (`id_materials`),
  UNIQUE KEY `id_materials_UNIQUE` (`id_materials`),
  UNIQUE KEY `name_materials_UNIQUE` (`name_materials`) /*!80000 INVISIBLE */,
  KEY `id_type_of_roofing_material_idx` (`id_type_of_roofing_material`),
  KEY `id_color_idx` (`id_color`),
  KEY `id_coverage_idx` (`id_coverage`),
  KEY `id_brand_idx` (`id_brand`),
  CONSTRAINT `id_brand` FOREIGN KEY (`id_brand`) REFERENCES `brand` (`id_brand`),
  CONSTRAINT `id_color` FOREIGN KEY (`id_color`) REFERENCES `color` (`id_color`),
  CONSTRAINT `id_coverage` FOREIGN KEY (`id_coverage`) REFERENCES `coverage` (`id_coverage`),
  CONSTRAINT `id_type_of_roofing_material` FOREIGN KEY (`id_type_of_roofing_material`) REFERENCES `type_of_roofing_material` (`id_type_of_roofing_material`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Кровельный лист КЛГ-001', '0.8', '2', '1', '1500', '1', '1', '1', '1');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Кровельный лист КЛГ-002', '0.8', '2', '1', '1500', '1', '2', '1', '1');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Кровельный лист КЛГ-003', '0.8', '2', '1', '1500', '1', '3', '1', '1');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Металл Профиль Ламонтерра (ПЭ-01-5002-0,5)', '0.5', '1', '1', '1200', '2', '4', '2', '2');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Металл Профиль Ламонтерра (ПЭ-01-6002-0,5)', '0.5', '1', '1', '1200', '2', '5', '2', '2');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Металл Профиль Монтерроса-XL (PURMAN-20-3005-0.4)', '0.4', '1', '1', '1100', '2', '6', '3', '2');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Металл Профиль Трамонтана-S (PURMAN-20-4005-0.4)', '0.4', '1', '1', '1100', '2', '5', '3', '2');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Фальцевая панель Металл Профиль FASTCLICK-T', '0.5', '1', '1', '1000', '3', '4', '2', '3');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Фальцевая панель Металл Профиль FASTCLICK (VikingMP-01-8017-0.45)', '0.5', '1', '1', '1000', '3', '3', '2', '3');
INSERT INTO `roofing_materials`.`materials` (`name_materials`, `thickness`, `place`, `count`, `price`, `id_type_of_roofing_material`, `id_color`, `id_coverage`, `id_brand`) VALUES ('Фальцевая панель Металл Профиль FASTCLICK-B NormanMP (ПЭ-01-7024-0,5)', '0.45', '1', '1', '900', '3', '2', '2', '3');


-- 6) роли:

CREATE TABLE `roofing_materials`.`roles` (
  `id_role` INT NOT NULL AUTO_INCREMENT,
  `name_role` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_role`),
  UNIQUE INDEX `id_role_UNIQUE` (`id_role` ASC) VISIBLE,
  UNIQUE INDEX `name_role_UNIQUE` (`name_role` ASC) VISIBLE);


INSERT INTO `roofing_materials`.`roles` (`name_role`) VALUES ('администратор');
INSERT INTO `roofing_materials`.`roles` (`name_role`) VALUES ('модератор');
INSERT INTO `roofing_materials`.`roles` (`name_role`) VALUES ('клиент');


-- 7) работники:

CREATE TABLE `roofing_materials`.`worker` (
  `id_worker` INT NOT NULL AUTO_INCREMENT,
  `firstname_worker` VARCHAR(100) NOT NULL,
  `lastname_worker` VARCHAR(100) NOT NULL,
  `login_worker` VARCHAR(100) NOT NULL,
  `password_worker` VARCHAR(200) NOT NULL,
  `id_role` INT NOT NULL,
  PRIMARY KEY (`id_worker`),
  UNIQUE INDEX `id_worker_UNIQUE` (`id_worker` ASC) VISIBLE,
  UNIQUE INDEX `login_worker_UNIQUE` (`login_worker` ASC) VISIBLE,
  INDEX `id_role_idx` (`id_role` ASC) VISIBLE,
  CONSTRAINT `id_role`
    FOREIGN KEY (`id_role`)
    REFERENCES `roofing_materials`.`roles` (`id_role`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);



-- 8) клиенты:

CREATE TABLE `client` (
  `id_client` int NOT NULL AUTO_INCREMENT,
  `firstname_client` varchar(100) NOT NULL,
  `lastname_client` varchar(100) NOT NULL,
  `phone_client` varchar(11) NOT NULL,
  `password_client` varchar(200) NOT NULL,
  `id_role` int NOT NULL DEFAULT '3',
  PRIMARY KEY (`id_client`),
  UNIQUE KEY `id_client_UNIQUE` (`id_client`),
  UNIQUE KEY `phone_client_UNIQUE` (`phone_client`),
  KEY `id_role3_idx` (`id_role`),
  CONSTRAINT `id_role3` FOREIGN KEY (`id_role`) REFERENCES `roles` (`id_role`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 9) Статусы заказов:
CREATE TABLE `order_status` (
  `id_status` INT NOT NULL AUTO_INCREMENT,
  `name_status` VARCHAR(50) NOT NULL, -- например: Новый, В обработке, Выполнен, Отменен
  PRIMARY KEY (`id_status`),
  UNIQUE KEY `name_status_UNIQUE` (`name_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `order_status` (`name_status`) VALUES 
('Новый'),
('В обработке'),
('Выполнен'),
('Отменен');

-- 10) Заказы:

CREATE TABLE `orders` (
  `id_order` INT NOT NULL AUTO_INCREMENT,
  `id_client` INT NOT NULL,
  `order_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_status` INT NOT NULL DEFAULT 1, -- по умолчанию "Новый"
  PRIMARY KEY (`id_order`),
  INDEX `idx_orders_client` (`id_client`),
  INDEX `idx_orders_status` (`id_status`),
  CONSTRAINT `fk_orders_client`
    FOREIGN KEY (`id_client`) REFERENCES `client`(`id_client`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_status`
    FOREIGN KEY (`id_status`) REFERENCES `order_status`(`id_status`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 11) Товары в заказе:

CREATE TABLE `order_items` (
  `id_order_item` INT NOT NULL AUTO_INCREMENT,
  `id_order` INT NOT NULL,
  `id_materials` INT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  `price` FLOAT NOT NULL, -- цена на момент заказа
  PRIMARY KEY (`id_order_item`),
  INDEX `id_order_idx` (`id_order`),
  INDEX `id_materials_idx` (`id_materials`),
  CONSTRAINT `fk_order_items_order`
    FOREIGN KEY (`id_order`)
    REFERENCES `orders` (`id_order`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_materials`
    FOREIGN KEY (`id_materials`)
    REFERENCES `materials` (`id_materials`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

