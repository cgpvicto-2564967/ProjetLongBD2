# =====================================
# = BOILERPLATE INITIALISATION PROJET =
# =====================================
import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, render_template, request

app = Flask(__name__)

# Charge les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupère les variables d'environnement
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

# Établir la connexion à la base de données
connexion = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name,
    port=db_port
)

# Vérifier si la connexion est établie
if connexion.is_connected():
    print("Connexion réussie à la base de données")
else:
    print("Échec de la connexion à la base de données")





# =======================================
# = Page d'accueil, formulaire commande =
# =======================================
# On va devoir aller chercher dans la base de données les garnitures, sauces et croutes qu'on a en stock
global garnitures
global sauces
global croutes

# Aller sur la page index.html
@app.route('/')
def index(resume = []):
    cursor = connexion.cursor(dictionary=True)

    # Aller chercher dans la base de données les garnitures, sauces et croutes qu'on a en stock
    cursor.execute("SELECT * FROM garniture")
    garnitures = cursor.fetchall()
    cursor.execute("SELECT * FROM sauce")
    sauces = cursor.fetchall()
    cursor.execute("SELECT * FROM croute")
    croutes = cursor.fetchall()

    # Aller chercher dans la base de donnée les pizza en attente de livraison
    # On a pas mal besoin de toute la BD pour les afficher...
    # Sauf bien sûr pour les pizzas qui ne sont pas en attente de livraison
    # Il faut des left join car certaines pizza n'ont pas de garnitures
    # Et le 2e left join sinon ça risque d'annuler le premier
    cursor.execute("""
    SELECT
        pizza.id AS idPizza,
        client.nom AS nomClient,
        client.adresse AS adresseClient,
        croute.nom AS nomCroute,
        sauce.nom AS nomSauce,
        garniture.nom as nomGarniture
    FROM commandes_attente_livraison
    JOIN pizza ON commandes_attente_livraison.id_pizza = pizza.id
    JOIN client ON pizza.id_client = client.id
    JOIN croute ON pizza.id_croute = croute.id
    JOIN sauce ON pizza.id_sauce = sauce.id
    LEFT JOIN garnitures_pour_pizza ON garnitures_pour_pizza.id_pizza = pizza.id
    LEFT JOIN garniture ON garnitures_pour_pizza.id_garniture = garniture.id
    """)
    attenteLivraison = cursor.fetchall()

    # Maintenant, il faut mettre les données dans le bon format avant de les envoyer au HTML:


    connexion.commit()
    cursor.close()

    # Envoit le client sur index.html et passes les autres données en argument dans le html pour jinja2 à afficher.
    return render_template(
        'index.html',
        garnitures = garnitures,
        sauces = sauces,
        croutes = croutes,
        resume = resume,
        attenteLivraison = attenteLivraison)



# =======================
# = Traitement commande =
# =======================
@app.route('/commander', methods=['POST'])
def commander():
    nom = request.form['nom']
    adresse = request.form['adresse']
    croute = request.form['croute']
    sauce = request.form['sauce']
    garnitures = [
        request.form['garniture0'],
        request.form['garniture1'],
        request.form['garniture2'],
        request.form['garniture3']
    ]
    idClient = None

    cursor = connexion.cursor(dictionary = True);

    
    try:
        connexion.start_transaction()

        # Étape 1 = client existe-t-il déjà? Select avec Where nom et adresse match
        # Syntaxe provenant de: https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html?utm_source=chatgpt.com
        cursor.execute("SELECT id FROM client WHERE nom = %s AND adresse = %s", (nom, adresse))
        clients = cursor.fetchall()
        if (len(clients) > 0):
            idClient = clients[0]["id"]

        # Étape 2 = Insert le cient s'il n'existe pas, puis on retient son ID
        if (idClient == None):
            cursor.execute("INSERT INTO client (nom, adresse) VALUES(%s, %s)", (nom, adresse))
            idClient = cursor.lastrowid

        # Étape 3 = Insert pizza avec l'ID du client
        cursor.execute("SELECT id FROM croute WHERE nom = %s", [croute])
        idCroute = cursor.fetchall()[0]["id"]
        cursor.execute("SELECT id FROM sauce WHERE nom = %s", [sauce])
        idSauce = cursor.fetchall()[0]["id"]
        cursor.execute("INSERT INTO pizza (id_client, id_croute, id_sauce) VALUES(%s, %s, %s)", (idClient, idCroute, idSauce))
        idPizza = cursor.lastrowid

        # Étape 4 = Insert les garnitures de la pizza
        for i in range(len(garnitures)):
            if (garnitures[i] != "aucun"):
                cursor.execute("SELECT * FROM garniture WHERE nom = %s", [garnitures[i]])
                idGarniture = cursor.fetchall()[0]["id"]
                cursor.execute("INSERT INTO garnitures_pour_pizza (id_pizza, id_garniture) VALUES(%s, %s)", (idPizza, idGarniture))

        # 5. Data à renvoyer pour afficher résumé de la commande
        resume = [nom, adresse, croute, sauce]
        for i in range(len(garnitures)):
            resume.append(garnitures[i])

        connexion.commit()
        cursor.close()
        return index(resume)
    except mysql.connector.Error as erreur:
        connexion.rollback()
        cursor.close()

        # Dans le résumé de la commende, écrire que la commende a échoué
        resume = [None] * 8
        for i in range(len(resume)):
            resume[i] = "Commande échouée."
        return index(resume)

    # NEXT: Appeler fonction pour append au html la nouvelle pizza






if __name__ == '__main__':
    app.run(debug=True)