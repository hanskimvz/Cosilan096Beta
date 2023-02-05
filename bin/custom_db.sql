-- MySQL dump 10.19  Distrib 10.3.28-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: cnt_demo
-- ------------------------------------------------------
-- Server version	10.3.28-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `age_gender`
--

DROP TABLE IF EXISTS `age_gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `age_gender` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `device_info` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `year` int(4) unsigned DEFAULT NULL,
  `month` int(2) unsigned DEFAULT NULL,
  `day` int(2) unsigned DEFAULT NULL,
  `hour` int(2) unsigned DEFAULT NULL,
  `min` int(2) unsigned DEFAULT NULL,
  `wday` int(1) unsigned DEFAULT NULL,
  `age_1st` int(10) unsigned DEFAULT 0,
  `age_2nd` int(10) unsigned DEFAULT 0,
  `age_3rd` int(10) unsigned DEFAULT 0,
  `age_4th` int(10) unsigned DEFAULT 0,
  `age_5th` int(10) unsigned DEFAULT 0,
  `age_6th` int(10) unsigned DEFAULT 0,
  `age_7th` int(10) unsigned DEFAULT 0,
  `male` int(10) unsigned DEFAULT 0,
  `female` int(10) unsigned DEFAULT 0,
  `age` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `week` int(2) DEFAULT NULL,
  `square_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `camera_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=66052 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `camera`
--

DROP TABLE IF EXISTS `camera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `camera` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `square_code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mac` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `brand` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `usn` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_id` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comment` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_countingline` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `enable_heatmap` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `enable_snapshot` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `enable_face_det` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `enable_macsniff` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `device_info` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `regdate` datetime DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `count_tenmin`
--

DROP TABLE IF EXISTS `count_tenmin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `count_tenmin` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `device_info` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `year` int(4) unsigned DEFAULT NULL,
  `month` int(2) unsigned DEFAULT NULL,
  `day` int(2) unsigned DEFAULT NULL,
  `hour` int(2) unsigned DEFAULT NULL,
  `min` int(2) unsigned DEFAULT NULL,
  `wday` int(1) unsigned DEFAULT NULL,
  `week` int(2) unsigned DEFAULT NULL,
  `counter_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `counter_val` int(11) unsigned DEFAULT NULL,
  `counter_label` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `camera_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `square_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=1012887 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counter_label`
--

DROP TABLE IF EXISTS `counter_label`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `counter_label` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `camera_code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `counter_name` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `counter_label` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'none',
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `face_analysis`
--

DROP TABLE IF EXISTS `face_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `face_analysis` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `regdate` datetime DEFAULT NULL,
  `thumbnail` blob DEFAULT NULL,
  `ref_face_token` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `face_token` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confidence` float unsigned DEFAULT NULL,
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  `date` datetime DEFAULT NULL,
  `face_thumbnail_pk` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=89581 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `face_set`
--

DROP TABLE IF EXISTS `face_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `face_set` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `regdate` datetime DEFAULT NULL,
  `thumbnail` blob DEFAULT NULL,
  `face_token` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `display_name` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `group_name` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `color` varchar(31) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `heatmap`
--

DROP TABLE IF EXISTS `heatmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `heatmap` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `device_info` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `year` int(4) unsigned DEFAULT NULL,
  `month` int(2) unsigned DEFAULT NULL,
  `day` int(2) unsigned DEFAULT NULL,
  `hour` int(2) unsigned DEFAULT NULL,
  `wday` int(1) unsigned DEFAULT NULL,
  `body_csv` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `week` int(2) unsigned DEFAULT NULL,
  `camera_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `square_code` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=74691 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `language`
--

DROP TABLE IF EXISTS `language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `language` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `varstr` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `eng` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `chi` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kor` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `page` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=711 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `realtime_counting`
--

DROP TABLE IF EXISTS `realtime_counting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `realtime_counting` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `day_before` int(2) unsigned DEFAULT 0,
  `ct_label` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `ct_value` int(11) DEFAULT 0,
  `latest` int(10) unsigned DEFAULT NULL,
  `ref_date` datetime DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `realtime_screen`
--

DROP TABLE IF EXISTS `realtime_screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `realtime_screen` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable` enum('yes','no') COLLATE utf8mb4_unicode_ci DEFAULT 'yes',
  `text` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `font` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `color` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `size` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `position` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `padding` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `ct_labels` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '["entrance", "exit"]',
  `rule` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `square`
--

DROP TABLE IF EXISTS `square`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `square` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_state` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_city` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_b` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comment` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `regdate` datetime DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `store`
--

DROP TABLE IF EXISTS `store`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `store` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `square_code` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_state` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_city` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `addr_b` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fax` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_person` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_tel` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `open_hour` smallint(6) DEFAULT NULL,
  `close_hour` smallint(6) DEFAULT NULL,
  `comment` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `regdate` datetime DEFAULT NULL,
  `sniffing_mac` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `area` int(10) unsigned DEFAULT NULL,
  `apply_open_hour` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name_eng` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telephone` varchar(127) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_b` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `theme` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT 'none',
  `date_in` date DEFAULT NULL,
  `date_out` date DEFAULT NULL,
  `img` mediumblob DEFAULT NULL,
  `comment` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weather`
--

DROP TABLE IF EXISTS `weather`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weather` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `timestamp` int(10) unsigned DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  `cityid` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cityCn` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `weather` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `temperature` int(3) DEFAULT NULL,
  `temp_low` int(3) DEFAULT NULL,
  `temp_high` int(3) DEFAULT NULL,
  `wind` varchar(31) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `humidity` int(3) DEFAULT NULL,
  `visibility` int(5) DEFAULT NULL,
  `pressure` int(5) DEFAULT NULL,
  `air` int(5) DEFAULT NULL,
  `air_pm25` int(5) DEFAULT NULL,
  `air_level` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=363 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `webpage_config`
--

DROP TABLE IF EXISTS `webpage_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webpage_config` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `page` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `frame` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `depth` int(10) DEFAULT 0,
  `pos_x` int(10) DEFAULT 0,
  `pos_y` int(10) DEFAULT 0,
  `body` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=244 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-01-29 23:52:46
