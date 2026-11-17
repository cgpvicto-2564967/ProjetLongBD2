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
    connexion.commit()
    cursor.close()

    # Envoit le client sur index.html et passes les autres données en argument dans le html pour jinja2 à afficher.
    return render_template(
        'index.html',
        garnitures = garnitures,
        sauces = sauces,
        croutes = croutes,
        resume = resume)



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
        cursor.execute(f"SELECT id FROM client WHERE nom = '{nom}' AND adresse = '{adresse}'")
        clients = cursor.fetchall()
        if (len(clients) > 0):
            idClient = clients[0]["id"]

        # Étape 2 = Insert le cient s'il n'existe pas, puis on retient son ID
        if (idClient == None):
            cursor.execute(f"INSERT INTO client (nom, adresse) VALUES('{nom}', '{adresse}')")
            idClient = cursor.lastrowid

        # Étape 3 = Insert pizza avec l'ID du client
        cursor.execute(f"SELECT id FROM croute WHERE nom = '{croute}'")
        idCroute = cursor.fetchall()[0]["id"]
        cursor.execute(f"SELECT id FROM sauce WHERE nom = '{sauce}'")
        idSauce = cursor.fetchall()[0]["id"]
        cursor.execute(f"INSERT INTO pizza (id_client, id_croute, id_sauce) VALUES('{idClient}', '{idCroute}', '{idSauce}')")
        idPizza = cursor.lastrowid

        # Étape 4 = Insert les garnitures de la pizza
        for i in range(len(garnitures)):
            if (garnitures[i] != "aucun"):
                cursor.execute(f"SELECT * FROM garniture WHERE nom = '{garnitures[i]}'")
                idGarniture = cursor.fetchall()[0]["id"]
                cursor.execute(f"INSERT INTO garnitures_pour_pizza (id_pizza, id_garniture) VALUES('{idPizza}', '{idGarniture}')")

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