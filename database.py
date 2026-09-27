from pprint import pprint
import sqlite3
import secrets
import hashlib


######## Initialize DataBase ###########
def init_db():
    conn = sqlite3.connect("aihost.db")
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL ,
        hash_key TEXT NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()

############ API ##############
def generate_api_key():
    token = secrets.token_urlsafe(32)
    return "sk_local_" + token


def hash_api_key(api_key):
    m = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return m

# put the hashing in the DB
def create_api_key(name):
    api_key = generate_api_key()
    hash_key = hash_api_key(api_key)
    init_db()

    conn = sqlite3.connect("aihost.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO api_keys(name, hash_key)
        VALUES (?, ?)
    """,
        (name, hash_key),
    )

    conn.commit()
    conn.close()

    return api_key

# check if the user's api matches the hash in the DB
def validate_api_key(api_key):
    hash_key = hash_api_key(api_key=api_key)
    conn = sqlite3.connect("aihost.db")
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, name FROM api_keys WHERE hash_key = ? AND is_active = 1""",
        (hash_key,),
    )
    a = cursor.fetchone()
    conn.close()
    return a


if __name__ == "__main__":
    init_db()
