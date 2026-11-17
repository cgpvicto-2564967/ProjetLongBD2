USE projet_long_pizza;

DELETE FROM garniture WHERE 1 = 1;
INSERT INTO garniture (nom) VALUES ("Pepperoni");
INSERT INTO garniture (nom) VALUES ("Champignons");
INSERT INTO garniture (nom) VALUES ("Oignons");
INSERT INTO garniture (nom) VALUES ("Poivrons");
INSERT INTO garniture (nom) VALUES ("Olives");
INSERT INTO garniture (nom) VALUES ("Anchois");
INSERT INTO garniture (nom) VALUES ("Bacon");
INSERT INTO garniture (nom) VALUES ("Poulet");
INSERT INTO garniture (nom) VALUES ("Maïs");
INSERT INTO garniture (nom) VALUES ("Fromage");
INSERT INTO garniture (nom) VALUES ("Piments forts");
SELECT * FROM garniture;

DELETE FROM croute WHERE 1 = 1;
INSERT INTO croute (nom) VALUES ("Classique");
INSERT INTO croute (nom) VALUES ("Mince");
INSERT INTO croute (nom) VALUES ("Épaisse");
SELECT * FROM croute;

DELETE FROM sauce WHERE 1 = 1;
INSERT INTO sauce (nom) VALUES ("Tomate");
INSERT INTO sauce (nom) VALUES ("Spaghetti");
INSERT INTO sauce (nom) VALUES ("Alfredo");
SELECT * FROM sauce;


SELECT * FROM `client`;
SELECT * FROM pizza;
SELECT * FROM garnitures_pour_pizza;


SELECT * FROM commandes_attente_livraison;