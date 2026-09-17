-- MySQL dump 10.13  Distrib 26.7.0, for macos15.7 (arm64)
--
-- Host: localhost    Database: veneer_business
-- ------------------------------------------------------
-- Server version	26.7.0

SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'cd1c3426-af9b-11f1-9293-316b886870fa:1-11';

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) NOT NULL,
  `city` varchar(50) DEFAULT NULL,
  `customer_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
INSERT INTO `customers` VALUES (1,'Himalayan Furniture Works','Kathmandu','Furniture Manufacturer'),(2,'Everest Timber Traders','Biratnagar','Wholesaler'),(3,'Jhapa Wood Crafts','Birtamode','Retailer'),(4,'Kaligandaki Interiors','Pokhara','Furniture Manufacturer'),(5,'Sunrise Plywood House','Itahari','Wholesaler'),(6,'Green Valley Furnishings','Dharan','Retailer'),(7,'Mount Makalu Traders','Damak','Wholesaler'),(8,'Royal Wood Interiors','Jhapa','Furniture Manufacturer');
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
INSERT INTO `products` VALUES (1,'Teak Veneer Grade A','Veneer',850.00),(2,'Teak Veneer Grade B','Veneer',620.00),(3,'Walnut Veneer Premium','Veneer',1100.00),(4,'Oak Veneer Standard','Veneer',540.00),(5,'Commercial Plywood 18mm','Plywood',1850.00),(6,'Marine Plywood 12mm','Plywood',2100.00),(7,'Laminate Sheet Glossy','Laminate',950.00),(8,'Laminate Sheet Matte','Laminate',890.00),(9,'Rosewood Veneer Deluxe','Veneer',1350.00),(10,'MDF Board 16mm','Board',1200.00);
UNLOCK TABLES;

--
-- Table structure for table `sales`
--

DROP TABLE IF EXISTS `sales`;
CREATE TABLE `sales` (
  `sale_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `sale_date` date NOT NULL,
  `quantity` int NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`sale_id`),
  KEY `customer_id` (`customer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `sales`
--

LOCK TABLES `sales` WRITE;
INSERT INTO `sales` VALUES (1,1,1,'2026-01-15',50,42500.00),(2,2,5,'2026-01-20',30,55500.00),(3,3,7,'2026-02-05',20,19000.00),(4,4,3,'2026-02-18',15,16500.00),(5,5,6,'2026-02-25',25,52500.00),(6,1,9,'2026-03-10',10,13500.00),(7,6,2,'2026-03-15',40,24800.00),(8,7,10,'2026-03-22',18,21600.00),(9,2,1,'2026-04-02',35,29750.00),(10,3,4,'2026-04-11',22,11880.00),(11,8,8,'2026-04-19',28,24920.00),(12,4,5,'2026-04-27',12,22200.00),(13,1,3,'2026-05-05',20,22000.00),(14,5,7,'2026-05-14',33,31350.00),(15,6,9,'2026-05-21',8,10800.00),(16,7,2,'2026-05-29',45,27900.00),(17,2,6,'2026-06-03',15,31500.00),(18,3,1,'2026-06-10',60,51000.00),(19,8,10,'2026-06-17',20,24000.00),(20,4,4,'2026-06-24',30,16200.00),(21,1,5,'2026-07-02',25,46250.00),(22,5,3,'2026-07-09',18,19800.00),(23,6,8,'2026-07-16',22,19580.00),(24,7,9,'2026-07-23',12,16200.00),(25,2,2,'2026-07-30',50,31000.00),(26,3,6,'2026-08-06',10,21000.00),(27,8,1,'2026-08-13',40,34000.00),(28,4,7,'2026-08-20',28,26600.00),(29,1,10,'2026-08-27',15,18000.00),(30,5,4,'2026-09-03',20,10800.00),(31,6,5,'2026-09-08',14,25900.00),(32,2,9,'2026-09-10',6,8100.00),(33,7,3,'2026-09-12',16,17600.00),(34,3,8,'2026-09-13',24,21360.00);
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;


-- Dump completed on 2026-09-17 12:13:33
