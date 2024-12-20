import sqlite3


class Database():

    def __init__(self):
        self.connection = None
        self.create_tables()

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/database.db')
        return self.connection

    def former_id(self, titre):
        if titre is None:
            return None
        return titre.lower().replace(' ', '')

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

    def create_tables(self):
        connection = self.get_connection()
        with open('db/utilisateurs.sql') as f:
            commands = f.read().split(';')
            for command in commands:
                if command.strip() != '':
                    connection.execute(command)
        connection.commit()

    def inserer_utilisateur(self, nom, courriel, mot_de_passe_hash,
                            mot_de_passe_salt, photo_de_profil):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Utilisateurs(nom, courriel, mot_de_passe_hash, mot_de_passe_salt, photo_de_profil) "
            "VALUES (?,?,?,?,?)",
            (nom, courriel, mot_de_passe_hash,
             mot_de_passe_salt, photo_de_profil)
        )
        connection.commit()
        return cursor.lastrowid

    def inserer_article(self, titre, auteur_id, date_de_publication, contenu):
        id_article = self.former_id(titre)
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Articles(identifiant, titre, auteur, "
            "date_de_publication, contenu) "
            "VALUES (?,?,?,?,?)",
            (id_article, titre, auteur_id, date_de_publication, contenu)
        )
        connection.commit()

    def article_info(self, id_article):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Articles WHERE id = ?", (id_article,))
        article_info = cursor.fetchone()
        return article_info

    def drop_utilisateurs_table(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DROP TABLE Utilisateurs;")
        connection.commit()

    def drop_articles_table(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DROP TABLE Articles;")
        connection.commit()

    def drop_sessions_table(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DROP TABLE Sessions;")
        connection.commit()

    def supprimer_tous_utilisateurs(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Utilisateurs;")
        connection.commit()

    def supprimer_tous_articles(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Articles;")
        connection.commit()

    def supprimer_tous_sessions(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Session;")
        connection.commit()

    def id_existe(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM Articles WHERE id = ?", (id,))
        return cursor.fetchone() is not None

    def nom_existe(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM UTILISATEURS WHERE nom LIKE?", ('%' + username + '%',))
        il_existe = cursor.fetchall()
        if len(il_existe) == 0:
            return False
        else:
            return True

    def login_info(self, username):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT mot_de_passe_hash, mot_de_passe_salt FROM Utilisateurs WHERE nom = ?", (username,))
        log_info = cursor.fetchone()
        if log_info is None:
            return None
        else:
            return log_info[0], log_info[1]

    def sauvegarder_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("INSERT INTO Sessions(id_session, nom) "
                            "VALUES(?, ?)"), (id_session, username))
        connection.commit()

    def __del__(self):
        self.close_connection()


db = Database()
db.supprimer_tous_utilisateurs()
db.supprimer_tous_articles()
# db.supprimer_tous_sessions()
db.drop_utilisateurs_table()
db.drop_articles_table()
db.drop_sessions_table()
db.create_tables()

# Exemple d'insertion
john_id = db.inserer_utilisateur("John",
                                 "john.doe@example.com",
                                 "hash1", "salt1", "/images/people-1.jpg")
alice_id = db.inserer_utilisateur("Alice",
                                  "alice.smith@example.com",
                                  "hash2", "salt2", "/images/people-2.jpg")
bob_id = db.inserer_utilisateur("Bob",
                                "bob.johnson@example.com",
                                "hash3", "salt3", "/images/people-3.jpg")
emily_id = db.inserer_utilisateur("Emily",
                                  "emily.brown@example.com",
                                  "hash4", "salt4", "/images/people-4.jpg")
david_id = db.inserer_utilisateur("David",
                                  "david.wilson@example.com",
                                  "hash5", "salt5", "/images/img-01.jpg")
sarah_id = db.inserer_utilisateur("Sarah",
                                  "sarah.anderson@example.com",
                                  "hash6", "salt6", "/images/img-03.jpg")
michael_id = db.inserer_utilisateur("prof",
                                    "prof@example.com",
                                    "secret", "1234", "/images/people-1.jpg")

db.inserer_article("Spiderman", "Marvel", "2024-03-07", "Content 1")
db.inserer_article("Sonic", "SEGA", "2024-02-17", "Content 2")
db.inserer_article("Luffy", "Echiro Oda", "2022-04-05", "Content 3")
db.inserer_article("Lebron James", "NBA", "1999-12-30", "Content 4")
db.inserer_article("Mario", "Nintendo", "2024-03-05", "Content 5")
db.inserer_article("Naruto", 'Kishimoto', "2024-03-07", "Content 6")
db.inserer_article("Goku", "Akira Toriyama", "2024-03-07", "Content 7")
db.inserer_article("FUTUUUURE", "Squidward (probably)", "2025-03-08", "Content 7")
