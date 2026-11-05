CREATE DATABASE IF NOT EXISTS projet_long_pizza;

USE projet_long_pizza;

DROP TABLE IF EXISTS garnitures_pour_pizza;
DROP TABLE IF EXISTS commandes_attente_livraison;
DROP TABLE IF EXISTS pizza;
DROP TABLE IF EXISTS garniture;
DROP TABLE IF EXISTS sauce;
DROP TABLE IF EXISTS croute;
DROP TABLE IF EXISTS `client`;

CREATE TABLE `client`(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL);

CREATE TABLE croute (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL);

CREATE TABLE sauce (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL);

CREATE TABLE garniture (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL);

CREATE TABLE pizza (
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_client INT,
    id_croute INT,
    id_sauce INT,
    FOREIGN KEY (id_client) REFERENCES `client` (id),
    FOREIGN KEY (id_croute) REFERENCES croute (id),
    FOREIGN KEY (id_sauce) REFERENCES sauce (id));

CREATE TABLE commandes_attente_livraison (
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_pizza INT,
    FOREIGN KEY (id_pizza) REFERENCES pizza(id));

CREATE TABLE garnitures_pour_pizza (
	id_pizza INT,
    id_garniture INT,
    PRIMARY KEY (id_pizza, id_garniture),
    FOREIGN KEY (id_pizza) REFERENCES pizza (id),
    FOREIGN KEY (id_garniture) REFERENCES garniture (id));

DROP TRIGGER IF EXISTS commande_en_attente;
DELIMITER $$
CREATE TRIGGER commande_en_attente
	AFTER INSERT
    ON pizza FOR EACH ROW
    BEGIN
		INSERT INTO commandes_attente_livraison (id_pizza)
        VALUES (NEW.id);
	END $$
DELIMITER ;