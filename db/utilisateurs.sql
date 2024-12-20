CREATE TABLE IF NOT EXISTS Utilisateurs (
    id INTEGER PRIMARY KEY,
    nom TEXT(100),
    courriel TEXT(100),
    mot_de_passe_hash TEXT NOT NULL,
    mot_de_passe_salt TEXT NOT NULL,
    photo_de_profil BLOB
);

CREATE TABLE IF NOT EXISTS Articles (
    id INTEGER PRIMARY KEY,
    identifiant TEXT,
    titre TEXT,
    auteur TEXT,
    date_de_publication DATE,
    contenu TEXT
);

CREATE TABLE IF NOT EXISTS Sessions (
  id INTEGER PRIMARY KEY,
  id_session VARCHAR(32),
  nom VARCHAR(25)
);
