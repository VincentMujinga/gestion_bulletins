-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: gestion_bulletins_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('a26cadf939cd');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demandes`
--

DROP TABLE IF EXISTS `demandes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `demandes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `annee_scolaire` varchar(20) NOT NULL,
  `date_demande` datetime DEFAULT NULL,
  `statut` varchar(50) DEFAULT NULL,
  `etablissement_id` int(11) NOT NULL,
  `processeur_id` int(11) DEFAULT NULL,
  `date_traitement` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `etablissement_id` (`etablissement_id`),
  KEY `ix_demandes_date_demande` (`date_demande`),
  KEY `processeur_id` (`processeur_id`),
  CONSTRAINT `demandes_ibfk_1` FOREIGN KEY (`etablissement_id`) REFERENCES `etablissements` (`id`),
  CONSTRAINT `demandes_ibfk_2` FOREIGN KEY (`processeur_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demandes`
--

LOCK TABLES `demandes` WRITE;
/*!40000 ALTER TABLE `demandes` DISABLE KEYS */;
INSERT INTO `demandes` VALUES (1,'2024-2025','2025-08-19 01:41:02','Traitée',2,8,'2025-08-20 20:45:52'),(2,'2024-2025','2025-08-19 02:36:38','Rejetée',2,NULL,NULL),(3,'2024-2025','2025-08-19 14:42:57','Traitée',2,8,'2025-08-20 21:02:10'),(4,'2024-2025','2025-08-19 15:00:21','Approuvée',2,6,'2025-08-19 21:07:11'),(5,'2024-2025','2025-08-19 15:11:13','Rejetée',2,6,'2025-08-19 20:44:22'),(6,'2024-2025','2025-08-19 21:05:21','Approuvée',2,6,'2025-08-19 21:51:11'),(7,'2024-2025','2025-08-20 00:42:23','Approuvée',2,6,'2025-08-20 00:58:15'),(8,'2024-2025','2025-08-20 00:51:06','Approuvée',2,6,'2025-08-20 00:58:23');
/*!40000 ALTER TABLE `demandes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etablissements`
--

DROP TABLE IF EXISTS `etablissements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `etablissements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(200) NOT NULL,
  `ville` varchar(100) DEFAULT NULL,
  `cecop` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom` (`nom`),
  UNIQUE KEY `cecop` (`cecop`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etablissements`
--

LOCK TABLES `etablissements` WRITE;
/*!40000 ALTER TABLE `etablissements` DISABLE KEYS */;
INSERT INTO `etablissements` VALUES (2,'mahidio','kamina','12273737'),(3,'LWANGA','kamina','773628929'),(4,'KITOKEJI','kamina','');
/*!40000 ALTER TABLE `etablissements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ligne_demandes`
--

DROP TABLE IF EXISTS `ligne_demandes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ligne_demandes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_ecole` varchar(50) NOT NULL,
  `niveau` varchar(50) NOT NULL,
  `option` varchar(100) DEFAULT NULL,
  `quantite` int(11) NOT NULL,
  `demande_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `demande_id` (`demande_id`),
  CONSTRAINT `ligne_demandes_ibfk_1` FOREIGN KEY (`demande_id`) REFERENCES `demandes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ligne_demandes`
--

LOCK TABLES `ligne_demandes` WRITE;
/*!40000 ALTER TABLE `ligne_demandes` DISABLE KEYS */;
INSERT INTO `ligne_demandes` VALUES (1,'Maternelle','1','',20,1),(2,'Maternelle','2','',44,1),(3,'Secondaire','1ère','Agronomie',122,2),(4,'Secondaire','2ème','Agronomie',123,2),(5,'Secondaire','3ème','Agronomie',424,2),(6,'Secondaire','4ème','Agronomie',132,2),(7,'Primaire','Moyen',NULL,123,3),(8,'Primaire','Élémentaire',NULL,123,3),(9,'Primaire','5ème',NULL,123,3),(10,'Primaire','6ème',NULL,1233,3),(11,'Secondaire','1ère','Agronomie',5365,4),(12,'Secondaire','2ème','Agronomie',425,4),(13,'Maternelle','1ère',NULL,122,5),(14,'Maternelle','2ème',NULL,1234,5),(15,'Maternelle','3ème',NULL,534,5),(16,'Primaire','Moyen',NULL,123,6),(17,'Primaire','5ème',NULL,1234,6),(18,'Secondaire','3ème','Commerciale et Gestion',455,7),(19,'Secondaire','2ème','Commerciale et Gestion',677,7),(20,'Secondaire','4ème','Commerciale et Gestion',556,7),(21,'Maternelle','1ère',NULL,1233,8),(22,'Maternelle','2ème',NULL,253,8),(23,'Maternelle','3ème',NULL,343,8);
/*!40000 ALTER TABLE `ligne_demandes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(512) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_notifications_timestamp` (`timestamp`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,'Bonne nouvelle ! Votre demande N°1 a été VALIDÉE par le Coordonnateur.','2025-08-19 14:57:18',1,4),(2,'Nouvelle demande (N°5) de mahidio à valider.','2025-08-19 15:11:13',1,5),(3,'Attention : Votre demande N°2 a été REJETÉE. Motif : formulaire incomplet: veiller completer votre demande','2025-08-19 15:31:14',1,4),(4,'Bonne nouvelle ! Votre demande N°3 a été VALIDÉE par le Coordonnateur.','2025-08-19 20:42:55',1,4),(5,'Bonne nouvelle ! Votre demande N°4 a été VALIDÉE par le Coordonnateur.','2025-08-19 20:43:02',1,4),(6,'Bonne nouvelle ! Votre demande N°5 a été VALIDÉE par le Coordonnateur.','2025-08-19 20:43:06',1,4),(7,'Excellente nouvelle ! Votre demande N°1 a été APPROUVÉE par le Sous-Proved.','2025-08-19 20:43:58',1,4),(8,'Excellente nouvelle ! Votre demande N°3 a été APPROUVÉE par le Sous-Proved.','2025-08-19 20:44:06',1,4),(9,'Attention : Votre demande N°5 a été REJETÉE par le Sous-Proved. Motif : non fonder','2025-08-19 20:44:22',1,4),(10,'Nouvelle demande (N°6) de mahidio à valider.','2025-08-19 21:05:21',1,5),(11,'Bonne nouvelle ! Votre demande N°6 a été VALIDÉE par le Coordonnateur.','2025-08-19 21:06:31',1,4),(12,'Excellente nouvelle ! Votre demande N°4 a été APPROUVÉE par le Sous-Proved.','2025-08-19 21:07:11',1,4),(13,'Info : La demande N°4 que vous aviez validée a été approuvée.','2025-08-19 21:07:11',1,5),(14,'Excellente nouvelle ! Votre demande N°6 a été APPROUVÉE par le Sous-Proved.','2025-08-19 21:51:11',1,4),(15,'Info : La demande N°6 que vous aviez validée a été approuvée.','2025-08-19 21:51:11',1,5),(16,'Nouvelle demande (N°7) de mahidio à valider.','2025-08-20 00:42:23',1,5),(17,'Bonne nouvelle ! Votre demande N°7 a été VALIDÉE par le Coordonnateur.','2025-08-20 00:43:35',1,4),(18,'Nouvelle demande (N°8) de mahidio à valider.','2025-08-20 00:51:06',1,5),(19,'Bonne nouvelle ! Votre demande N°8 a été VALIDÉE par le Coordonnateur.','2025-08-20 00:51:34',1,4),(20,'Nouvelle demande (N°8) de mahidio à approuver.','2025-08-20 00:51:34',1,6),(21,'Excellente nouvelle ! Votre demande N°7 a été APPROUVÉE par le Sous-Proved.','2025-08-20 00:58:15',0,4),(22,'Info : La demande N°7 que vous aviez validée a été approuvée.','2025-08-20 00:58:15',1,5),(23,'Excellente nouvelle ! Votre demande N°8 a été APPROUVÉE par le Sous-Proved.','2025-08-20 00:58:23',0,4),(24,'Info : La demande N°8 que vous aviez validée a été approuvée.','2025-08-20 00:58:23',1,5),(25,'Votre demande N°1 a été TRAITÉE. Les bulletins sont prêts pour la distribution.','2025-08-20 20:45:52',0,4),(26,'Votre demande N°3 a été TRAITÉE. Les bulletins sont prêts pour la distribution.','2025-08-20 21:02:10',0,4);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrateur'),(2,'Chef d\'établissement'),(3,'Coordonnateur'),(5,'Proved'),(4,'Sous-Proved');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `role_id` int(11) NOT NULL,
  `etablissement_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `role_id` (`role_id`),
  KEY `etablissement_id` (`etablissement_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`etablissement_id`) REFERENCES `etablissements` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@example.com','scrypt:32768:8:1$g0OIDyIrtyS0NmWQ$4b1cefd1e2fcf798e46d12b8a9dd045169ba2707671eca2f321968bf712f778e6cc839c6a0f11c775eb7806de7c2950a5a82b2982de45c6fbf2c4f1030255617',1,NULL),(4,'monga','mchrisluvi@gmail.com','scrypt:32768:8:1$sObrlwy8HiJuu91G$7b4979e6d61e25e73da665cc36ad522479b81d90bab00c502064de2b2d52fccd3e59bb0b1bd98c775ba144dc690067faf680a4b1ce28fb4b46d6ad403936f7d2',2,2),(5,'mujinga','mongavincent286@gmail.com','scrypt:32768:8:1$e0GWr3G2HGRJuaqH$b064f501f2e8da609ecc1c02ac2135f245d3a46084b64f6a0dfd2e4adac22737f303ca6e4360105da58b78516c54bed5b0e1cbfc53ababfbdaa112a993dd72d4',3,NULL),(6,'sous-proved','mongavincent2865@gmail.com','scrypt:32768:8:1$v1IvMJpM3HIxXjBJ$063c7a5b559d96b7bc31a8f4fb0884d0d51acfe041ff495944c2ab69ae162c641c0b44461c4b71ffa29292c4373024f35b5e03b23dbec50cd2becdbe6ed8d562',4,NULL),(7,'adalber','mchrisluvi123@gmail.com','scrypt:32768:8:1$JNY7q4Su2lJAftQY$7868ba4d44fcf4162c95e5cc40b760cd976beed862b9dd3c27c0aff11abea7edf331c045061f4cfa3d606ca2d41b80ac00b77cd39eab623e701f36ac84d3d61c',2,3),(8,'proved','mchrisluvi1223@gmail.com','scrypt:32768:8:1$EiBJguxtaPGwInA9$3881bdd34c127cd1ab3c23047006c8569aca58d3ad7548043d2ac2d509710b4ca575e30755a57cc83f129b929b7bb40f01fa0226c98af741cb34aece5d7cdc28',5,NULL),(9,'coordonnateur','mongavincent222286@gmail.com','scrypt:32768:8:1$3rgNqkgYBBlFA0HP$dfda27af45d01463de4a76064c8f78b4eeb663dad49a66a2cd114eb2f820807a74f60947eb81c05b4c99881b83eb2cc599c4391cc5f8479cc3d373d033624046',3,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-21  2:03:58
