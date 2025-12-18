import sqlite3
import random

DB_NAME = 'user.db'

modele = [
        "YAMAHA", "bob", "the best", "the fast" , "drakar", "siperrapid", "letrorapid",
        "YAMAHAmaismieux", "lemoyenrapid", "lebofrapid", "siperultramegafast", "AAAAAAAAAA",
        "y'avaitplusdenom", "huh",
    ]

def insert_random_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor

    for i in range(100):
        modele = random.choice(modele) + "V" + str(random.randint(1,999))
        temps = random.randint(1000, 10000) + "Secondes"

        try:
            cursor.execute("INSERT INTO velos (modele) VALUES (?)", (modele))
            cursor.execute("INSERT INTO parcours (temps) VALUES (?)", (temps))
        except:
            continue

    conn.commit()
    conn.close()
    print("100 donnés ajoutées sur la database")

insert_random_users()