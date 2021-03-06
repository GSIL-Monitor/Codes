-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: 192.168.1.208    Database: tshbao
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
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location` (
  `locationId` int(11) NOT NULL,
  `locationName` varchar(100) NOT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  `modifyTime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`locationId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location`
--

LOCK TABLES `location` WRITE;
/*!40000 ALTER TABLE `location` DISABLE KEYS */;
INSERT INTO `location` VALUES (0,'未知',NULL,NULL),(1,'北京',NULL,NULL),(2,'上海',NULL,NULL),(4,'天津',NULL,NULL),(6,'重庆',NULL,NULL),(7,'安徽',NULL,NULL),(8,'合肥',NULL,NULL),(9,'宿州',NULL,NULL),(10,'淮北',NULL,NULL),(11,'阜阳',NULL,NULL),(12,'亳州',NULL,NULL),(13,'蚌埠',NULL,NULL),(14,'淮南',NULL,NULL),(15,'滁州',NULL,NULL),(16,'马鞍山',NULL,NULL),(17,'芜湖',NULL,NULL),(18,'铜陵',NULL,NULL),(19,'安庆',NULL,NULL),(20,'黄山',NULL,NULL),(21,'六安',NULL,NULL),(22,'巢湖',NULL,NULL),(23,'池州',NULL,NULL),(24,'宣城',NULL,NULL),(25,'澳门',NULL,NULL),(26,'福建',NULL,NULL),(27,'福州',NULL,NULL),(28,'南平',NULL,NULL),(29,'三明',NULL,NULL),(30,'莆田',NULL,NULL),(31,'泉州',NULL,NULL),(32,'厦门',NULL,NULL),(33,'漳州',NULL,NULL),(34,'龙岩',NULL,NULL),(35,'宁德',NULL,NULL),(36,'甘肃',NULL,NULL),(37,'兰州',NULL,NULL),(38,'嘉峪关',NULL,NULL),(39,'金昌',NULL,NULL),(40,'白银',NULL,NULL),(41,'天水',NULL,NULL),(42,'武威',NULL,NULL),(43,'酒泉',NULL,NULL),(44,'张掖',NULL,NULL),(45,'庆阳',NULL,NULL),(46,'平凉',NULL,NULL),(47,'定西',NULL,NULL),(48,'陇南',NULL,NULL),(49,'临夏州',NULL,NULL),(50,'甘南州',NULL,NULL),(51,'广东',NULL,NULL),(52,'广州',NULL,NULL),(53,'清远',NULL,NULL),(54,'韶关',NULL,NULL),(55,'河源',NULL,NULL),(56,'梅州',NULL,NULL),(57,'潮州',NULL,NULL),(58,'汕头',NULL,NULL),(59,'揭阳',NULL,NULL),(60,'汕尾',NULL,NULL),(61,'惠州',NULL,NULL),(62,'东莞',NULL,NULL),(63,'深圳',NULL,NULL),(64,'珠海',NULL,NULL),(65,'中山',NULL,NULL),(66,'江门',NULL,NULL),(67,'佛山',NULL,NULL),(68,'肇庆',NULL,NULL),(69,'云浮',NULL,NULL),(70,'阳江',NULL,NULL),(71,'茂名',NULL,NULL),(72,'湛江',NULL,NULL),(73,'广西',NULL,NULL),(74,'南宁',NULL,NULL),(75,'桂林',NULL,NULL),(76,'柳州',NULL,NULL),(77,'梧州',NULL,NULL),(78,'贵港',NULL,NULL),(79,'玉林',NULL,NULL),(80,'钦州',NULL,NULL),(81,'北海',NULL,NULL),(82,'防城港',NULL,NULL),(83,'崇左',NULL,NULL),(84,'百色',NULL,NULL),(85,'河池',NULL,NULL),(86,'来宾',NULL,NULL),(87,'贺州',NULL,NULL),(88,'贵州',NULL,NULL),(89,'贵阳',NULL,NULL),(90,'六盘水',NULL,NULL),(91,'遵义',NULL,NULL),(92,'安顺',NULL,NULL),(93,'毕节',NULL,NULL),(94,'铜仁',NULL,NULL),(95,'黔东南州',NULL,NULL),(96,'黔南州',NULL,NULL),(97,'黔西南州',NULL,NULL),(98,'海南',NULL,NULL),(99,'海口',NULL,NULL),(100,'三亚',NULL,NULL),(101,'河北',NULL,NULL),(102,'石家庄',NULL,NULL),(103,'张家口',NULL,NULL),(104,'承德',NULL,NULL),(105,'秦皇岛',NULL,NULL),(106,'唐山',NULL,NULL),(107,'廊坊',NULL,NULL),(108,'保定',NULL,NULL),(109,'沧州',NULL,NULL),(110,'衡水',NULL,NULL),(111,'邢台',NULL,NULL),(112,'邯郸',NULL,NULL),(113,'河南',NULL,NULL),(114,'郑州',NULL,NULL),(115,'三门峡',NULL,NULL),(116,'洛阳',NULL,NULL),(117,'焦作',NULL,NULL),(118,'新乡',NULL,NULL),(119,'鹤壁',NULL,NULL),(120,'安阳',NULL,NULL),(121,'濮阳',NULL,NULL),(122,'开封',NULL,NULL),(123,'商丘',NULL,NULL),(124,'许昌',NULL,NULL),(125,'漯河',NULL,NULL),(126,'平顶山',NULL,NULL),(127,'南阳',NULL,NULL),(128,'信阳',NULL,NULL),(129,'周口',NULL,NULL),(130,'驻马店',NULL,NULL),(131,'黑龙江',NULL,NULL),(132,'哈尔滨',NULL,NULL),(133,'齐齐哈尔',NULL,NULL),(134,'黑河',NULL,NULL),(135,'大庆',NULL,NULL),(136,'伊春',NULL,NULL),(137,'鹤岗',NULL,NULL),(138,'佳木斯',NULL,NULL),(139,'双鸭山',NULL,NULL),(140,'七台河',NULL,NULL),(141,'鸡西',NULL,NULL),(142,'牡丹江',NULL,NULL),(143,'绥化',NULL,NULL),(144,'大兴安岭',NULL,NULL),(145,'湖北',NULL,NULL),(146,'武汉',NULL,NULL),(147,'十堰',NULL,NULL),(148,'襄阳',NULL,NULL),(149,'荆门',NULL,NULL),(150,'孝感',NULL,NULL),(151,'黄冈',NULL,NULL),(152,'鄂州',NULL,NULL),(153,'黄石',NULL,NULL),(154,'咸宁',NULL,NULL),(155,'荆州',NULL,NULL),(156,'宜昌',NULL,NULL),(157,'随州',NULL,NULL),(158,'恩施州',NULL,NULL),(159,'湖南',NULL,NULL),(160,'长沙',NULL,NULL),(161,'张家界',NULL,NULL),(162,'常德',NULL,NULL),(163,'益阳',NULL,NULL),(164,'岳阳',NULL,NULL),(165,'株洲',NULL,NULL),(166,'湘潭',NULL,NULL),(167,'衡阳',NULL,NULL),(168,'郴州',NULL,NULL),(169,'永州',NULL,NULL),(170,'邵阳',NULL,NULL),(171,'怀化',NULL,NULL),(172,'娄底',NULL,NULL),(173,'湘西州',NULL,NULL),(174,'吉林',NULL,NULL),(175,'长春',NULL,NULL),(176,'白城',NULL,NULL),(177,'松原',NULL,NULL),(179,'四平',NULL,NULL),(180,'辽源',NULL,NULL),(181,'通化',NULL,NULL),(182,'白山',NULL,NULL),(183,'延边州',NULL,NULL),(184,'江苏',NULL,NULL),(185,'南京',NULL,NULL),(186,'徐州',NULL,NULL),(187,'连云港',NULL,NULL),(188,'宿迁',NULL,NULL),(189,'淮安',NULL,NULL),(190,'盐城',NULL,NULL),(191,'扬州',NULL,NULL),(192,'泰州',NULL,NULL),(193,'南通',NULL,NULL),(194,'镇江',NULL,NULL),(195,'常州',NULL,NULL),(196,'无锡',NULL,NULL),(197,'苏州',NULL,NULL),(198,'江西',NULL,NULL),(199,'南昌',NULL,NULL),(200,'九江',NULL,NULL),(201,'景德镇',NULL,NULL),(202,'鹰潭',NULL,NULL),(203,'新余',NULL,NULL),(204,'萍乡',NULL,NULL),(205,'赣州',NULL,NULL),(206,'上饶',NULL,NULL),(207,'抚州',NULL,NULL),(208,'宜春',NULL,NULL),(209,'吉安',NULL,NULL),(210,'辽宁',NULL,NULL),(211,'沈阳',NULL,NULL),(212,'朝阳',NULL,NULL),(213,'阜新',NULL,NULL),(214,'铁岭',NULL,NULL),(215,'抚顺',NULL,NULL),(216,'本溪',NULL,NULL),(217,'辽阳',NULL,NULL),(218,'鞍山',NULL,NULL),(219,'丹东',NULL,NULL),(220,'大连',NULL,NULL),(221,'营口',NULL,NULL),(222,'盘锦',NULL,NULL),(223,'锦州',NULL,NULL),(224,'葫芦岛',NULL,NULL),(225,'内蒙古',NULL,NULL),(226,'呼和浩特',NULL,NULL),(227,'包头',NULL,NULL),(228,'乌海',NULL,NULL),(229,'赤峰',NULL,NULL),(230,'通辽',NULL,NULL),(231,'呼伦贝尔',NULL,NULL),(232,'鄂尔多斯',NULL,NULL),(233,'乌兰察布',NULL,NULL),(234,'巴彦淖尔',NULL,NULL),(235,'兴安盟',NULL,NULL),(236,'锡林郭勒',NULL,NULL),(237,'阿拉善盟',NULL,NULL),(238,'宁夏',NULL,NULL),(239,'银川',NULL,NULL),(240,'石嘴山',NULL,NULL),(241,'吴忠',NULL,NULL),(242,'固原',NULL,NULL),(243,'中卫',NULL,NULL),(244,'青海',NULL,NULL),(245,'西宁',NULL,NULL),(246,'海东',NULL,NULL),(247,'海北州',NULL,NULL),(248,'海南州',NULL,NULL),(249,'黄南州',NULL,NULL),(250,'果洛州',NULL,NULL),(251,'玉树州',NULL,NULL),(252,'海西州',NULL,NULL),(253,'山东',NULL,NULL),(254,'济南',NULL,NULL),(255,'聊城',NULL,NULL),(256,'德州',NULL,NULL),(257,'东营',NULL,NULL),(258,'淄博',NULL,NULL),(259,'潍坊',NULL,NULL),(260,'烟台',NULL,NULL),(261,'威海',NULL,NULL),(262,'青岛',NULL,NULL),(263,'日照',NULL,NULL),(264,'临沂',NULL,NULL),(265,'枣庄',NULL,NULL),(266,'济宁',NULL,NULL),(267,'泰安',NULL,NULL),(268,'莱芜',NULL,NULL),(269,'滨州',NULL,NULL),(270,'菏泽',NULL,NULL),(271,'山西',NULL,NULL),(272,'太原',NULL,NULL),(273,'大同',NULL,NULL),(274,'朔州',NULL,NULL),(275,'阳泉',NULL,NULL),(276,'长治',NULL,NULL),(277,'晋城',NULL,NULL),(278,'忻州',NULL,NULL),(279,'晋中',NULL,NULL),(280,'临汾',NULL,NULL),(281,'运城',NULL,NULL),(282,'吕梁',NULL,NULL),(283,'陕西',NULL,NULL),(284,'西安',NULL,NULL),(285,'延安',NULL,NULL),(286,'铜川',NULL,NULL),(287,'渭南',NULL,NULL),(288,'咸阳',NULL,NULL),(289,'宝鸡',NULL,NULL),(290,'汉中',NULL,NULL),(291,'榆林',NULL,NULL),(292,'安康',NULL,NULL),(294,'商洛',NULL,NULL),(295,'四川',NULL,NULL),(296,'成都',NULL,NULL),(297,'广元',NULL,NULL),(298,'绵阳',NULL,NULL),(299,'德阳',NULL,NULL),(300,'南充',NULL,NULL),(301,'广安',NULL,NULL),(302,'遂宁',NULL,NULL),(303,'内江',NULL,NULL),(304,'乐山',NULL,NULL),(305,'自贡',NULL,NULL),(306,'泸州',NULL,NULL),(307,'宜宾',NULL,NULL),(308,'攀枝花',NULL,NULL),(309,'巴中',NULL,NULL),(310,'达州',NULL,NULL),(311,'资阳',NULL,NULL),(312,'眉山',NULL,NULL),(313,'雅安',NULL,NULL),(314,'阿坝州',NULL,NULL),(315,'甘孜州',NULL,NULL),(316,'凉山州',NULL,NULL),(317,'台湾',NULL,NULL),(318,'西藏',NULL,NULL),(319,'拉萨',NULL,NULL),(320,'那曲',NULL,NULL),(321,'昌都',NULL,NULL),(322,'林芝',NULL,NULL),(323,'山南',NULL,NULL),(324,'日喀则',NULL,NULL),(325,'阿里',NULL,NULL),(326,'香港',NULL,NULL),(327,'新疆',NULL,NULL),(328,'乌鲁木齐',NULL,NULL),(329,'克拉玛依',NULL,NULL),(330,'喀什',NULL,NULL),(331,'阿克苏',NULL,NULL),(332,'和田',NULL,NULL),(333,'吐鲁番',NULL,NULL),(334,'哈密',NULL,NULL),(335,'克孜勒苏',NULL,NULL),(336,'博尔塔拉',NULL,NULL),(337,'昌吉州',NULL,NULL),(338,'巴音郭楞',NULL,NULL),(339,'伊犁州',NULL,NULL),(340,'塔城',NULL,NULL),(341,'阿勒泰',NULL,NULL),(342,'云南',NULL,NULL),(343,'昆明',NULL,NULL),(344,'曲靖',NULL,NULL),(345,'玉溪',NULL,NULL),(346,'保山',NULL,NULL),(347,'昭通',NULL,NULL),(348,'丽江',NULL,NULL),(349,'思茅',NULL,NULL),(350,'临沧',NULL,NULL),(351,'德宏州',NULL,NULL),(352,'怒江州',NULL,NULL),(353,'迪庆州',NULL,NULL),(354,'大理州',NULL,NULL),(355,'楚雄州',NULL,NULL),(356,'红河州',NULL,NULL),(357,'文山州',NULL,NULL),(358,'西双版纳',NULL,NULL),(359,'浙江',NULL,NULL),(360,'杭州',NULL,NULL),(361,'湖州',NULL,NULL),(362,'嘉兴',NULL,NULL),(363,'舟山',NULL,NULL),(364,'宁波',NULL,NULL),(365,'绍兴',NULL,NULL),(366,'衢州',NULL,NULL),(367,'金华',NULL,NULL),(368,'台州',NULL,NULL),(369,'温州',NULL,NULL),(370,'丽水',NULL,NULL),(371,'意大利',NULL,NULL),(372,'比利时',NULL,NULL),(373,'希腊',NULL,NULL),(374,'葡萄牙',NULL,NULL),(375,'西班牙',NULL,NULL),(376,'捷克',NULL,NULL),(377,'波兰',NULL,NULL),(378,'瑞士',NULL,NULL),(379,'挪威',NULL,NULL),(380,'瑞典',NULL,NULL),(381,'卢森堡',NULL,NULL),(382,'乌克兰',NULL,NULL),(383,'荷兰',NULL,NULL),(384,'英国',NULL,NULL),(385,'丹麦',NULL,NULL),(386,'奥地利',NULL,NULL),(387,'阿根廷',NULL,NULL),(388,'巴西',NULL,NULL),(389,'智利',NULL,NULL),(390,'委内瑞拉',NULL,NULL),(391,'哥伦比亚',NULL,NULL),(392,'乌拉圭',NULL,NULL),(393,'沙特',NULL,NULL),(394,'马来西亚',NULL,NULL),(395,'阿联酋',NULL,NULL),(396,'印尼',NULL,NULL),(397,'泰国',NULL,NULL),(398,'印度',NULL,NULL),(399,'新加坡',NULL,NULL),(400,'韩国',NULL,NULL),(401,'日本',NULL,NULL),(402,'墨西哥',NULL,NULL),(403,'加拿大',NULL,NULL),(404,'美国',NULL,NULL),(405,'新西兰',NULL,NULL),(406,'澳大利亚',NULL,NULL),(407,'摩洛哥',NULL,NULL),(408,'尼日利亚',NULL,NULL),(409,'埃及',NULL,NULL),(410,'南非',NULL,NULL),(411,'德国',NULL,NULL);
/*!40000 ALTER TABLE `location` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-17 16:06:10
