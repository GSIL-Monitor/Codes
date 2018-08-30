-- MySQL dump 10.13  Distrib 5.6.22, for osx10.8 (x86_64)
--
-- Host: 192.168.1.208    Database: crawler_v2
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alexa1`
--

DROP TABLE IF EXISTS `alexa1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa10`
--

DROP TABLE IF EXISTS `alexa10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa100`
--

DROP TABLE IF EXISTS `alexa100`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa100` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa11`
--

DROP TABLE IF EXISTS `alexa11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa12`
--

DROP TABLE IF EXISTS `alexa12`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa13`
--

DROP TABLE IF EXISTS `alexa13`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa14`
--

DROP TABLE IF EXISTS `alexa14`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa15`
--

DROP TABLE IF EXISTS `alexa15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa16`
--

DROP TABLE IF EXISTS `alexa16`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa17`
--

DROP TABLE IF EXISTS `alexa17`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa17` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa18`
--

DROP TABLE IF EXISTS `alexa18`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa18` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa19`
--

DROP TABLE IF EXISTS `alexa19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa19` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa2`
--

DROP TABLE IF EXISTS `alexa2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa20`
--

DROP TABLE IF EXISTS `alexa20`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa20` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa21`
--

DROP TABLE IF EXISTS `alexa21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa22`
--

DROP TABLE IF EXISTS `alexa22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa23`
--

DROP TABLE IF EXISTS `alexa23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa24`
--

DROP TABLE IF EXISTS `alexa24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa25`
--

DROP TABLE IF EXISTS `alexa25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa25` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa26`
--

DROP TABLE IF EXISTS `alexa26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa26` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa27`
--

DROP TABLE IF EXISTS `alexa27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa27` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa28`
--

DROP TABLE IF EXISTS `alexa28`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa28` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa29`
--

DROP TABLE IF EXISTS `alexa29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa29` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa3`
--

DROP TABLE IF EXISTS `alexa3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa30`
--

DROP TABLE IF EXISTS `alexa30`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa30` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa31`
--

DROP TABLE IF EXISTS `alexa31`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa31` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa32`
--

DROP TABLE IF EXISTS `alexa32`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa32` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa33`
--

DROP TABLE IF EXISTS `alexa33`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa33` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa34`
--

DROP TABLE IF EXISTS `alexa34`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa34` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa35`
--

DROP TABLE IF EXISTS `alexa35`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa35` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa36`
--

DROP TABLE IF EXISTS `alexa36`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa36` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa37`
--

DROP TABLE IF EXISTS `alexa37`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa37` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa38`
--

DROP TABLE IF EXISTS `alexa38`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa38` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa39`
--

DROP TABLE IF EXISTS `alexa39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa39` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa4`
--

DROP TABLE IF EXISTS `alexa4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa40`
--

DROP TABLE IF EXISTS `alexa40`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa40` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa41`
--

DROP TABLE IF EXISTS `alexa41`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa41` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa42`
--

DROP TABLE IF EXISTS `alexa42`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa42` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa43`
--

DROP TABLE IF EXISTS `alexa43`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa43` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa44`
--

DROP TABLE IF EXISTS `alexa44`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa44` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa45`
--

DROP TABLE IF EXISTS `alexa45`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa45` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa46`
--

DROP TABLE IF EXISTS `alexa46`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa46` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa47`
--

DROP TABLE IF EXISTS `alexa47`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa47` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa48`
--

DROP TABLE IF EXISTS `alexa48`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa48` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa49`
--

DROP TABLE IF EXISTS `alexa49`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa49` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa5`
--

DROP TABLE IF EXISTS `alexa5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa50`
--

DROP TABLE IF EXISTS `alexa50`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa50` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa51`
--

DROP TABLE IF EXISTS `alexa51`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa51` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa52`
--

DROP TABLE IF EXISTS `alexa52`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa52` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa53`
--

DROP TABLE IF EXISTS `alexa53`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa53` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa54`
--

DROP TABLE IF EXISTS `alexa54`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa54` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa55`
--

DROP TABLE IF EXISTS `alexa55`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa55` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa56`
--

DROP TABLE IF EXISTS `alexa56`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa56` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa57`
--

DROP TABLE IF EXISTS `alexa57`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa57` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa58`
--

DROP TABLE IF EXISTS `alexa58`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa58` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa59`
--

DROP TABLE IF EXISTS `alexa59`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa59` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa6`
--

DROP TABLE IF EXISTS `alexa6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa60`
--

DROP TABLE IF EXISTS `alexa60`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa60` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa61`
--

DROP TABLE IF EXISTS `alexa61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa61` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa62`
--

DROP TABLE IF EXISTS `alexa62`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa62` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa63`
--

DROP TABLE IF EXISTS `alexa63`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa63` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa64`
--

DROP TABLE IF EXISTS `alexa64`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa64` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa65`
--

DROP TABLE IF EXISTS `alexa65`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa65` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa66`
--

DROP TABLE IF EXISTS `alexa66`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa66` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa67`
--

DROP TABLE IF EXISTS `alexa67`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa67` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa68`
--

DROP TABLE IF EXISTS `alexa68`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa68` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa69`
--

DROP TABLE IF EXISTS `alexa69`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa69` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa7`
--

DROP TABLE IF EXISTS `alexa7`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa70`
--

DROP TABLE IF EXISTS `alexa70`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa70` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa71`
--

DROP TABLE IF EXISTS `alexa71`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa71` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa72`
--

DROP TABLE IF EXISTS `alexa72`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa72` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa73`
--

DROP TABLE IF EXISTS `alexa73`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa73` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa74`
--

DROP TABLE IF EXISTS `alexa74`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa74` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa75`
--

DROP TABLE IF EXISTS `alexa75`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa75` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa76`
--

DROP TABLE IF EXISTS `alexa76`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa76` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa77`
--

DROP TABLE IF EXISTS `alexa77`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa77` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa78`
--

DROP TABLE IF EXISTS `alexa78`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa78` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa79`
--

DROP TABLE IF EXISTS `alexa79`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa79` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa8`
--

DROP TABLE IF EXISTS `alexa8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa80`
--

DROP TABLE IF EXISTS `alexa80`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa80` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa81`
--

DROP TABLE IF EXISTS `alexa81`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa81` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa82`
--

DROP TABLE IF EXISTS `alexa82`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa82` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa83`
--

DROP TABLE IF EXISTS `alexa83`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa83` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa84`
--

DROP TABLE IF EXISTS `alexa84`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa84` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa85`
--

DROP TABLE IF EXISTS `alexa85`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa85` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa86`
--

DROP TABLE IF EXISTS `alexa86`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa86` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa87`
--

DROP TABLE IF EXISTS `alexa87`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa87` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa88`
--

DROP TABLE IF EXISTS `alexa88`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa88` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa89`
--

DROP TABLE IF EXISTS `alexa89`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa89` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa9`
--

DROP TABLE IF EXISTS `alexa9`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa90`
--

DROP TABLE IF EXISTS `alexa90`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa90` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa91`
--

DROP TABLE IF EXISTS `alexa91`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa91` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa92`
--

DROP TABLE IF EXISTS `alexa92`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa92` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa93`
--

DROP TABLE IF EXISTS `alexa93`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa93` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa94`
--

DROP TABLE IF EXISTS `alexa94`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa94` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa95`
--

DROP TABLE IF EXISTS `alexa95`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa95` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa96`
--

DROP TABLE IF EXISTS `alexa96`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa96` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa97`
--

DROP TABLE IF EXISTS `alexa97`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa97` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa98`
--

DROP TABLE IF EXISTS `alexa98`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa98` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alexa99`
--

DROP TABLE IF EXISTS `alexa99`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alexa99` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) DEFAULT NULL,
  `rankCN` int(11) DEFAULT NULL,
  `rankGlobal` int(11) DEFAULT NULL,
  `dailyIP` int(11) DEFAULT NULL,
  `dailyPV` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android1`
--

DROP TABLE IF EXISTS `android1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android10`
--

DROP TABLE IF EXISTS `android10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android100`
--

DROP TABLE IF EXISTS `android100`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android100` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android11`
--

DROP TABLE IF EXISTS `android11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android12`
--

DROP TABLE IF EXISTS `android12`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android13`
--

DROP TABLE IF EXISTS `android13`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android14`
--

DROP TABLE IF EXISTS `android14`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android15`
--

DROP TABLE IF EXISTS `android15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android16`
--

DROP TABLE IF EXISTS `android16`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android17`
--

DROP TABLE IF EXISTS `android17`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android17` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android18`
--

DROP TABLE IF EXISTS `android18`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android18` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android19`
--

DROP TABLE IF EXISTS `android19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android19` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android2`
--

DROP TABLE IF EXISTS `android2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android20`
--

DROP TABLE IF EXISTS `android20`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android20` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android21`
--

DROP TABLE IF EXISTS `android21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android22`
--

DROP TABLE IF EXISTS `android22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android23`
--

DROP TABLE IF EXISTS `android23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android24`
--

DROP TABLE IF EXISTS `android24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android25`
--

DROP TABLE IF EXISTS `android25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android25` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android26`
--

DROP TABLE IF EXISTS `android26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android26` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android27`
--

DROP TABLE IF EXISTS `android27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android27` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android28`
--

DROP TABLE IF EXISTS `android28`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android28` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android29`
--

DROP TABLE IF EXISTS `android29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android29` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android3`
--

DROP TABLE IF EXISTS `android3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android30`
--

DROP TABLE IF EXISTS `android30`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android30` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android31`
--

DROP TABLE IF EXISTS `android31`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android31` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android32`
--

DROP TABLE IF EXISTS `android32`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android32` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android33`
--

DROP TABLE IF EXISTS `android33`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android33` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android34`
--

DROP TABLE IF EXISTS `android34`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android34` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android35`
--

DROP TABLE IF EXISTS `android35`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android35` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android36`
--

DROP TABLE IF EXISTS `android36`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android36` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android37`
--

DROP TABLE IF EXISTS `android37`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android37` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android38`
--

DROP TABLE IF EXISTS `android38`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android38` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android39`
--

DROP TABLE IF EXISTS `android39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android39` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android4`
--

DROP TABLE IF EXISTS `android4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android40`
--

DROP TABLE IF EXISTS `android40`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android40` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android41`
--

DROP TABLE IF EXISTS `android41`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android41` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android42`
--

DROP TABLE IF EXISTS `android42`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android42` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android43`
--

DROP TABLE IF EXISTS `android43`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android43` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android44`
--

DROP TABLE IF EXISTS `android44`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android44` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android45`
--

DROP TABLE IF EXISTS `android45`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android45` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android46`
--

DROP TABLE IF EXISTS `android46`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android46` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android47`
--

DROP TABLE IF EXISTS `android47`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android47` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android48`
--

DROP TABLE IF EXISTS `android48`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android48` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android49`
--

DROP TABLE IF EXISTS `android49`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android49` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android5`
--

DROP TABLE IF EXISTS `android5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android50`
--

DROP TABLE IF EXISTS `android50`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android50` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android51`
--

DROP TABLE IF EXISTS `android51`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android51` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android52`
--

DROP TABLE IF EXISTS `android52`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android52` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android53`
--

DROP TABLE IF EXISTS `android53`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android53` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android54`
--

DROP TABLE IF EXISTS `android54`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android54` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android55`
--

DROP TABLE IF EXISTS `android55`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android55` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android56`
--

DROP TABLE IF EXISTS `android56`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android56` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android57`
--

DROP TABLE IF EXISTS `android57`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android57` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android58`
--

DROP TABLE IF EXISTS `android58`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android58` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android59`
--

DROP TABLE IF EXISTS `android59`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android59` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android6`
--

DROP TABLE IF EXISTS `android6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android60`
--

DROP TABLE IF EXISTS `android60`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android60` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android61`
--

DROP TABLE IF EXISTS `android61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android61` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android62`
--

DROP TABLE IF EXISTS `android62`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android62` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android63`
--

DROP TABLE IF EXISTS `android63`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android63` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android64`
--

DROP TABLE IF EXISTS `android64`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android64` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android65`
--

DROP TABLE IF EXISTS `android65`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android65` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android66`
--

DROP TABLE IF EXISTS `android66`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android66` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android67`
--

DROP TABLE IF EXISTS `android67`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android67` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android68`
--

DROP TABLE IF EXISTS `android68`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android68` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android69`
--

DROP TABLE IF EXISTS `android69`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android69` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android7`
--

DROP TABLE IF EXISTS `android7`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android70`
--

DROP TABLE IF EXISTS `android70`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android70` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android71`
--

DROP TABLE IF EXISTS `android71`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android71` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android72`
--

DROP TABLE IF EXISTS `android72`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android72` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android73`
--

DROP TABLE IF EXISTS `android73`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android73` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android74`
--

DROP TABLE IF EXISTS `android74`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android74` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android75`
--

DROP TABLE IF EXISTS `android75`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android75` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android76`
--

DROP TABLE IF EXISTS `android76`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android76` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android77`
--

DROP TABLE IF EXISTS `android77`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android77` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android78`
--

DROP TABLE IF EXISTS `android78`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android78` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android79`
--

DROP TABLE IF EXISTS `android79`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android79` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android8`
--

DROP TABLE IF EXISTS `android8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android80`
--

DROP TABLE IF EXISTS `android80`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android80` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android81`
--

DROP TABLE IF EXISTS `android81`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android81` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android82`
--

DROP TABLE IF EXISTS `android82`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android82` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android83`
--

DROP TABLE IF EXISTS `android83`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android83` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android84`
--

DROP TABLE IF EXISTS `android84`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android84` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android85`
--

DROP TABLE IF EXISTS `android85`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android85` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android86`
--

DROP TABLE IF EXISTS `android86`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android86` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android87`
--

DROP TABLE IF EXISTS `android87`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android87` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android88`
--

DROP TABLE IF EXISTS `android88`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android88` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android89`
--

DROP TABLE IF EXISTS `android89`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android89` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android9`
--

DROP TABLE IF EXISTS `android9`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android90`
--

DROP TABLE IF EXISTS `android90`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android90` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android91`
--

DROP TABLE IF EXISTS `android91`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android91` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android92`
--

DROP TABLE IF EXISTS `android92`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android92` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android93`
--

DROP TABLE IF EXISTS `android93`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android93` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android94`
--

DROP TABLE IF EXISTS `android94`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android94` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android95`
--

DROP TABLE IF EXISTS `android95`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android95` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android96`
--

DROP TABLE IF EXISTS `android96`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android96` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android97`
--

DROP TABLE IF EXISTS `android97`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android97` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android98`
--

DROP TABLE IF EXISTS `android98`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android98` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `android99`
--

DROP TABLE IF EXISTS `android99`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `android99` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `download` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company_index`
--

DROP TABLE IF EXISTS `company_index`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `company_index` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `alexa` int(11) DEFAULT NULL,
  `adnroid` int(11) DEFAULT NULL,
  `ios` int(11) DEFAULT NULL,
  `job` int(11) DEFAULT NULL,
  `news` int(11) DEFAULT NULL,
  `wechat` int(11) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dictionary`
--

DROP TABLE IF EXISTS `dictionary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dictionary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` int(11) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `typeValue` int(11) DEFAULT NULL,
  `typeName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios1`
--

DROP TABLE IF EXISTS `ios1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios10`
--

DROP TABLE IF EXISTS `ios10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios100`
--

DROP TABLE IF EXISTS `ios100`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios100` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios11`
--

DROP TABLE IF EXISTS `ios11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios12`
--

DROP TABLE IF EXISTS `ios12`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios13`
--

DROP TABLE IF EXISTS `ios13`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios14`
--

DROP TABLE IF EXISTS `ios14`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios15`
--

DROP TABLE IF EXISTS `ios15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios16`
--

DROP TABLE IF EXISTS `ios16`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios17`
--

DROP TABLE IF EXISTS `ios17`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios17` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios18`
--

DROP TABLE IF EXISTS `ios18`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios18` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios19`
--

DROP TABLE IF EXISTS `ios19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios19` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios2`
--

DROP TABLE IF EXISTS `ios2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios20`
--

DROP TABLE IF EXISTS `ios20`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios20` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios21`
--

DROP TABLE IF EXISTS `ios21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios22`
--

DROP TABLE IF EXISTS `ios22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios23`
--

DROP TABLE IF EXISTS `ios23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios24`
--

DROP TABLE IF EXISTS `ios24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios25`
--

DROP TABLE IF EXISTS `ios25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios25` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios26`
--

DROP TABLE IF EXISTS `ios26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios26` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios27`
--

DROP TABLE IF EXISTS `ios27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios27` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios28`
--

DROP TABLE IF EXISTS `ios28`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios28` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios29`
--

DROP TABLE IF EXISTS `ios29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios29` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios3`
--

DROP TABLE IF EXISTS `ios3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios30`
--

DROP TABLE IF EXISTS `ios30`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios30` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios31`
--

DROP TABLE IF EXISTS `ios31`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios31` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios32`
--

DROP TABLE IF EXISTS `ios32`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios32` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios33`
--

DROP TABLE IF EXISTS `ios33`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios33` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios34`
--

DROP TABLE IF EXISTS `ios34`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios34` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios35`
--

DROP TABLE IF EXISTS `ios35`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios35` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios36`
--

DROP TABLE IF EXISTS `ios36`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios36` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios37`
--

DROP TABLE IF EXISTS `ios37`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios37` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios38`
--

DROP TABLE IF EXISTS `ios38`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios38` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios39`
--

DROP TABLE IF EXISTS `ios39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios39` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios4`
--

DROP TABLE IF EXISTS `ios4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios40`
--

DROP TABLE IF EXISTS `ios40`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios40` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios41`
--

DROP TABLE IF EXISTS `ios41`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios41` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios42`
--

DROP TABLE IF EXISTS `ios42`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios42` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios43`
--

DROP TABLE IF EXISTS `ios43`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios43` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios44`
--

DROP TABLE IF EXISTS `ios44`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios44` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios45`
--

DROP TABLE IF EXISTS `ios45`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios45` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios46`
--

DROP TABLE IF EXISTS `ios46`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios46` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios47`
--

DROP TABLE IF EXISTS `ios47`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios47` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios48`
--

DROP TABLE IF EXISTS `ios48`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios48` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios49`
--

DROP TABLE IF EXISTS `ios49`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios49` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios5`
--

DROP TABLE IF EXISTS `ios5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios50`
--

DROP TABLE IF EXISTS `ios50`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios50` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios51`
--

DROP TABLE IF EXISTS `ios51`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios51` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios52`
--

DROP TABLE IF EXISTS `ios52`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios52` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios53`
--

DROP TABLE IF EXISTS `ios53`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios53` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios54`
--

DROP TABLE IF EXISTS `ios54`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios54` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios55`
--

DROP TABLE IF EXISTS `ios55`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios55` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios56`
--

DROP TABLE IF EXISTS `ios56`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios56` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios57`
--

DROP TABLE IF EXISTS `ios57`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios57` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios58`
--

DROP TABLE IF EXISTS `ios58`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios58` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios59`
--

DROP TABLE IF EXISTS `ios59`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios59` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios6`
--

DROP TABLE IF EXISTS `ios6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios60`
--

DROP TABLE IF EXISTS `ios60`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios60` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios61`
--

DROP TABLE IF EXISTS `ios61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios61` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios62`
--

DROP TABLE IF EXISTS `ios62`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios62` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios63`
--

DROP TABLE IF EXISTS `ios63`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios63` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios64`
--

DROP TABLE IF EXISTS `ios64`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios64` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios65`
--

DROP TABLE IF EXISTS `ios65`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios65` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios66`
--

DROP TABLE IF EXISTS `ios66`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios66` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios67`
--

DROP TABLE IF EXISTS `ios67`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios67` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios68`
--

DROP TABLE IF EXISTS `ios68`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios68` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios69`
--

DROP TABLE IF EXISTS `ios69`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios69` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios7`
--

DROP TABLE IF EXISTS `ios7`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios70`
--

DROP TABLE IF EXISTS `ios70`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios70` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios71`
--

DROP TABLE IF EXISTS `ios71`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios71` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios72`
--

DROP TABLE IF EXISTS `ios72`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios72` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios73`
--

DROP TABLE IF EXISTS `ios73`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios73` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios74`
--

DROP TABLE IF EXISTS `ios74`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios74` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios75`
--

DROP TABLE IF EXISTS `ios75`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios75` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios76`
--

DROP TABLE IF EXISTS `ios76`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios76` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios77`
--

DROP TABLE IF EXISTS `ios77`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios77` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios78`
--

DROP TABLE IF EXISTS `ios78`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios78` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios79`
--

DROP TABLE IF EXISTS `ios79`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios79` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios8`
--

DROP TABLE IF EXISTS `ios8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios80`
--

DROP TABLE IF EXISTS `ios80`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios80` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios81`
--

DROP TABLE IF EXISTS `ios81`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios81` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios82`
--

DROP TABLE IF EXISTS `ios82`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios82` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios83`
--

DROP TABLE IF EXISTS `ios83`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios83` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios84`
--

DROP TABLE IF EXISTS `ios84`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios84` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios85`
--

DROP TABLE IF EXISTS `ios85`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios85` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios86`
--

DROP TABLE IF EXISTS `ios86`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios86` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios87`
--

DROP TABLE IF EXISTS `ios87`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios87` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios88`
--

DROP TABLE IF EXISTS `ios88`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios88` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios89`
--

DROP TABLE IF EXISTS `ios89`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios89` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios9`
--

DROP TABLE IF EXISTS `ios9`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios90`
--

DROP TABLE IF EXISTS `ios90`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios90` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios91`
--

DROP TABLE IF EXISTS `ios91`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios91` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios92`
--

DROP TABLE IF EXISTS `ios92`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios92` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios93`
--

DROP TABLE IF EXISTS `ios93`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios93` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios94`
--

DROP TABLE IF EXISTS `ios94`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios94` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios95`
--

DROP TABLE IF EXISTS `ios95`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios95` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios96`
--

DROP TABLE IF EXISTS `ios96`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios96` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios97`
--

DROP TABLE IF EXISTS `ios97`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios97` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios98`
--

DROP TABLE IF EXISTS `ios98`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios98` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ios99`
--

DROP TABLE IF EXISTS `ios99`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ios99` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) NOT NULL,
  `artifactId` int(11) NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `comment` int(11) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`),
  KEY `index2` (`companyId`,`artifactId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `job`
--

DROP TABLE IF EXISTS `job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `job` (
  `id` int(11) NOT NULL,
  `companyId` int(11) DEFAULT NULL,
  `jobId` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news1`
--

DROP TABLE IF EXISTS `news1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news10`
--

DROP TABLE IF EXISTS `news10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news100`
--

DROP TABLE IF EXISTS `news100`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news100` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news11`
--

DROP TABLE IF EXISTS `news11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news12`
--

DROP TABLE IF EXISTS `news12`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news13`
--

DROP TABLE IF EXISTS `news13`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news14`
--

DROP TABLE IF EXISTS `news14`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news15`
--

DROP TABLE IF EXISTS `news15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news16`
--

DROP TABLE IF EXISTS `news16`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news17`
--

DROP TABLE IF EXISTS `news17`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news17` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news18`
--

DROP TABLE IF EXISTS `news18`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news18` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news19`
--

DROP TABLE IF EXISTS `news19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news19` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news2`
--

DROP TABLE IF EXISTS `news2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news20`
--

DROP TABLE IF EXISTS `news20`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news20` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news21`
--

DROP TABLE IF EXISTS `news21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news22`
--

DROP TABLE IF EXISTS `news22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news23`
--

DROP TABLE IF EXISTS `news23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news24`
--

DROP TABLE IF EXISTS `news24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news25`
--

DROP TABLE IF EXISTS `news25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news25` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news26`
--

DROP TABLE IF EXISTS `news26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news26` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news27`
--

DROP TABLE IF EXISTS `news27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news27` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news28`
--

DROP TABLE IF EXISTS `news28`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news28` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news29`
--

DROP TABLE IF EXISTS `news29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news29` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news3`
--

DROP TABLE IF EXISTS `news3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news30`
--

DROP TABLE IF EXISTS `news30`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news30` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news31`
--

DROP TABLE IF EXISTS `news31`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news31` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news32`
--

DROP TABLE IF EXISTS `news32`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news32` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news33`
--

DROP TABLE IF EXISTS `news33`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news33` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news34`
--

DROP TABLE IF EXISTS `news34`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news34` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news35`
--

DROP TABLE IF EXISTS `news35`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news35` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news36`
--

DROP TABLE IF EXISTS `news36`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news36` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news37`
--

DROP TABLE IF EXISTS `news37`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news37` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news38`
--

DROP TABLE IF EXISTS `news38`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news38` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news39`
--

DROP TABLE IF EXISTS `news39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news39` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news4`
--

DROP TABLE IF EXISTS `news4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news40`
--

DROP TABLE IF EXISTS `news40`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news40` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news41`
--

DROP TABLE IF EXISTS `news41`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news41` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news42`
--

DROP TABLE IF EXISTS `news42`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news42` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news43`
--

DROP TABLE IF EXISTS `news43`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news43` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news44`
--

DROP TABLE IF EXISTS `news44`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news44` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news45`
--

DROP TABLE IF EXISTS `news45`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news45` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news46`
--

DROP TABLE IF EXISTS `news46`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news46` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news47`
--

DROP TABLE IF EXISTS `news47`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news47` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news48`
--

DROP TABLE IF EXISTS `news48`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news48` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news49`
--

DROP TABLE IF EXISTS `news49`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news49` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news5`
--

DROP TABLE IF EXISTS `news5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news50`
--

DROP TABLE IF EXISTS `news50`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news50` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news51`
--

DROP TABLE IF EXISTS `news51`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news51` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news52`
--

DROP TABLE IF EXISTS `news52`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news52` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news53`
--

DROP TABLE IF EXISTS `news53`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news53` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news54`
--

DROP TABLE IF EXISTS `news54`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news54` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news55`
--

DROP TABLE IF EXISTS `news55`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news55` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news56`
--

DROP TABLE IF EXISTS `news56`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news56` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news57`
--

DROP TABLE IF EXISTS `news57`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news57` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news58`
--

DROP TABLE IF EXISTS `news58`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news58` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news59`
--

DROP TABLE IF EXISTS `news59`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news59` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news6`
--

DROP TABLE IF EXISTS `news6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news60`
--

DROP TABLE IF EXISTS `news60`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news60` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news61`
--

DROP TABLE IF EXISTS `news61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news61` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news62`
--

DROP TABLE IF EXISTS `news62`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news62` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news63`
--

DROP TABLE IF EXISTS `news63`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news63` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news64`
--

DROP TABLE IF EXISTS `news64`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news64` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news65`
--

DROP TABLE IF EXISTS `news65`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news65` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news66`
--

DROP TABLE IF EXISTS `news66`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news66` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news67`
--

DROP TABLE IF EXISTS `news67`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news67` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news68`
--

DROP TABLE IF EXISTS `news68`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news68` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news69`
--

DROP TABLE IF EXISTS `news69`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news69` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news7`
--

DROP TABLE IF EXISTS `news7`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news70`
--

DROP TABLE IF EXISTS `news70`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news70` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news71`
--

DROP TABLE IF EXISTS `news71`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news71` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news72`
--

DROP TABLE IF EXISTS `news72`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news72` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news73`
--

DROP TABLE IF EXISTS `news73`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news73` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news74`
--

DROP TABLE IF EXISTS `news74`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news74` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news75`
--

DROP TABLE IF EXISTS `news75`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news75` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news76`
--

DROP TABLE IF EXISTS `news76`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news76` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news77`
--

DROP TABLE IF EXISTS `news77`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news77` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news78`
--

DROP TABLE IF EXISTS `news78`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news78` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news79`
--

DROP TABLE IF EXISTS `news79`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news79` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news8`
--

DROP TABLE IF EXISTS `news8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news80`
--

DROP TABLE IF EXISTS `news80`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news80` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news81`
--

DROP TABLE IF EXISTS `news81`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news81` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news82`
--

DROP TABLE IF EXISTS `news82`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news82` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news83`
--

DROP TABLE IF EXISTS `news83`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news83` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news84`
--

DROP TABLE IF EXISTS `news84`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news84` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news85`
--

DROP TABLE IF EXISTS `news85`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news85` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news86`
--

DROP TABLE IF EXISTS `news86`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news86` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news87`
--

DROP TABLE IF EXISTS `news87`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news87` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news88`
--

DROP TABLE IF EXISTS `news88`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news88` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news89`
--

DROP TABLE IF EXISTS `news89`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news89` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news9`
--

DROP TABLE IF EXISTS `news9`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news90`
--

DROP TABLE IF EXISTS `news90`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news90` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news91`
--

DROP TABLE IF EXISTS `news91`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news91` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news92`
--

DROP TABLE IF EXISTS `news92`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news92` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news93`
--

DROP TABLE IF EXISTS `news93`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news93` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news94`
--

DROP TABLE IF EXISTS `news94`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news94` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news95`
--

DROP TABLE IF EXISTS `news95`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news95` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news96`
--

DROP TABLE IF EXISTS `news96`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news96` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news97`
--

DROP TABLE IF EXISTS `news97`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news97` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news98`
--

DROP TABLE IF EXISTS `news98`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news98` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news99`
--

DROP TABLE IF EXISTS `news99`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news99` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `companyId` int(11) DEFAULT NULL,
  `domainId` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `link` varchar(200) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`companyId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content1`
--

DROP TABLE IF EXISTS `news_content1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content10`
--

DROP TABLE IF EXISTS `news_content10`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content100`
--

DROP TABLE IF EXISTS `news_content100`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content100` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content11`
--

DROP TABLE IF EXISTS `news_content11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content12`
--

DROP TABLE IF EXISTS `news_content12`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content13`
--

DROP TABLE IF EXISTS `news_content13`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content14`
--

DROP TABLE IF EXISTS `news_content14`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content15`
--

DROP TABLE IF EXISTS `news_content15`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content16`
--

DROP TABLE IF EXISTS `news_content16`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content17`
--

DROP TABLE IF EXISTS `news_content17`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content17` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content18`
--

DROP TABLE IF EXISTS `news_content18`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content18` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content19`
--

DROP TABLE IF EXISTS `news_content19`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content19` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content2`
--

DROP TABLE IF EXISTS `news_content2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content20`
--

DROP TABLE IF EXISTS `news_content20`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content20` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content21`
--

DROP TABLE IF EXISTS `news_content21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content22`
--

DROP TABLE IF EXISTS `news_content22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content23`
--

DROP TABLE IF EXISTS `news_content23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content24`
--

DROP TABLE IF EXISTS `news_content24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content25`
--

DROP TABLE IF EXISTS `news_content25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content25` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content26`
--

DROP TABLE IF EXISTS `news_content26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content26` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content27`
--

DROP TABLE IF EXISTS `news_content27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content27` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content28`
--

DROP TABLE IF EXISTS `news_content28`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content28` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content29`
--

DROP TABLE IF EXISTS `news_content29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content29` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content3`
--

DROP TABLE IF EXISTS `news_content3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content30`
--

DROP TABLE IF EXISTS `news_content30`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content30` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content31`
--

DROP TABLE IF EXISTS `news_content31`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content31` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content32`
--

DROP TABLE IF EXISTS `news_content32`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content32` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content33`
--

DROP TABLE IF EXISTS `news_content33`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content33` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content34`
--

DROP TABLE IF EXISTS `news_content34`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content34` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content35`
--

DROP TABLE IF EXISTS `news_content35`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content35` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content36`
--

DROP TABLE IF EXISTS `news_content36`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content36` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content37`
--

DROP TABLE IF EXISTS `news_content37`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content37` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content38`
--

DROP TABLE IF EXISTS `news_content38`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content38` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content39`
--

DROP TABLE IF EXISTS `news_content39`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content39` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content4`
--

DROP TABLE IF EXISTS `news_content4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content40`
--

DROP TABLE IF EXISTS `news_content40`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content40` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content41`
--

DROP TABLE IF EXISTS `news_content41`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content41` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content42`
--

DROP TABLE IF EXISTS `news_content42`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content42` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content43`
--

DROP TABLE IF EXISTS `news_content43`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content43` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content44`
--

DROP TABLE IF EXISTS `news_content44`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content44` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content45`
--

DROP TABLE IF EXISTS `news_content45`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content45` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content46`
--

DROP TABLE IF EXISTS `news_content46`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content46` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content47`
--

DROP TABLE IF EXISTS `news_content47`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content47` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content48`
--

DROP TABLE IF EXISTS `news_content48`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content48` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content49`
--

DROP TABLE IF EXISTS `news_content49`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content49` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content5`
--

DROP TABLE IF EXISTS `news_content5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content50`
--

DROP TABLE IF EXISTS `news_content50`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content50` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content51`
--

DROP TABLE IF EXISTS `news_content51`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content51` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content52`
--

DROP TABLE IF EXISTS `news_content52`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content52` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content53`
--

DROP TABLE IF EXISTS `news_content53`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content53` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content54`
--

DROP TABLE IF EXISTS `news_content54`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content54` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content55`
--

DROP TABLE IF EXISTS `news_content55`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content55` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content56`
--

DROP TABLE IF EXISTS `news_content56`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content56` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content57`
--

DROP TABLE IF EXISTS `news_content57`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content57` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content58`
--

DROP TABLE IF EXISTS `news_content58`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content58` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content59`
--

DROP TABLE IF EXISTS `news_content59`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content59` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content6`
--

DROP TABLE IF EXISTS `news_content6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content60`
--

DROP TABLE IF EXISTS `news_content60`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content60` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content61`
--

DROP TABLE IF EXISTS `news_content61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content61` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content62`
--

DROP TABLE IF EXISTS `news_content62`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content62` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content63`
--

DROP TABLE IF EXISTS `news_content63`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content63` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content64`
--

DROP TABLE IF EXISTS `news_content64`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content64` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content65`
--

DROP TABLE IF EXISTS `news_content65`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content65` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content66`
--

DROP TABLE IF EXISTS `news_content66`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content66` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content67`
--

DROP TABLE IF EXISTS `news_content67`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content67` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content68`
--

DROP TABLE IF EXISTS `news_content68`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content68` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content69`
--

DROP TABLE IF EXISTS `news_content69`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content69` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content7`
--

DROP TABLE IF EXISTS `news_content7`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content70`
--

DROP TABLE IF EXISTS `news_content70`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content70` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content71`
--

DROP TABLE IF EXISTS `news_content71`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content71` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content72`
--

DROP TABLE IF EXISTS `news_content72`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content72` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content73`
--

DROP TABLE IF EXISTS `news_content73`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content73` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content74`
--

DROP TABLE IF EXISTS `news_content74`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content74` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content75`
--

DROP TABLE IF EXISTS `news_content75`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content75` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content76`
--

DROP TABLE IF EXISTS `news_content76`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content76` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content77`
--

DROP TABLE IF EXISTS `news_content77`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content77` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content78`
--

DROP TABLE IF EXISTS `news_content78`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content78` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content79`
--

DROP TABLE IF EXISTS `news_content79`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content79` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content8`
--

DROP TABLE IF EXISTS `news_content8`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content80`
--

DROP TABLE IF EXISTS `news_content80`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content80` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content81`
--

DROP TABLE IF EXISTS `news_content81`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content81` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content82`
--

DROP TABLE IF EXISTS `news_content82`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content82` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content83`
--

DROP TABLE IF EXISTS `news_content83`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content83` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content84`
--

DROP TABLE IF EXISTS `news_content84`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content84` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content85`
--

DROP TABLE IF EXISTS `news_content85`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content85` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content86`
--

DROP TABLE IF EXISTS `news_content86`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content86` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content87`
--

DROP TABLE IF EXISTS `news_content87`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content87` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content88`
--

DROP TABLE IF EXISTS `news_content88`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content88` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content89`
--

DROP TABLE IF EXISTS `news_content89`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content89` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content9`
--

DROP TABLE IF EXISTS `news_content9`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content90`
--

DROP TABLE IF EXISTS `news_content90`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content90` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content91`
--

DROP TABLE IF EXISTS `news_content91`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content91` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content92`
--

DROP TABLE IF EXISTS `news_content92`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content92` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content93`
--

DROP TABLE IF EXISTS `news_content93`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content93` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content94`
--

DROP TABLE IF EXISTS `news_content94`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content94` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content95`
--

DROP TABLE IF EXISTS `news_content95`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content95` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content96`
--

DROP TABLE IF EXISTS `news_content96`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content96` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content97`
--

DROP TABLE IF EXISTS `news_content97`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content97` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content98`
--

DROP TABLE IF EXISTS `news_content98`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content98` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_content99`
--

DROP TABLE IF EXISTS `news_content99`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_content99` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) NOT NULL,
  `content` text,
  `image` varchar(200) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index1` (`newsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_domain`
--

DROP TABLE IF EXISTS `news_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `netloc` varchar(200) DEFAULT NULL,
  `domain` varchar(100) DEFAULT NULL,
  `title` varchar(45) DEFAULT NULL,
  `appearCount` int(11) DEFAULT NULL,
  `hintCount` int(11) DEFAULT NULL,
  `confidence` char(1) DEFAULT NULL,
  `verify` char(1) DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news_latest`
--

DROP TABLE IF EXISTS `news_latest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news_latest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `newsId` int(11) DEFAULT NULL,
  `newsTable` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `active` char(1) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  `createUser` int(11) DEFAULT NULL,
  `modifyUser` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proxy`
--

DROP TABLE IF EXISTS `proxy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) DEFAULT NULL,
  `port` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `anonymity` varchar(45) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1529 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wechat`
--

DROP TABLE IF EXISTS `wechat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wechat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `zhihu`
--

DROP TABLE IF EXISTS `zhihu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zhihu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-13 16:11:18
