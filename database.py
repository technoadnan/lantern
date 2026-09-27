from pprint import pprint
import sqlite3
import secrets
import hashlib


def get_db_connection():
    conn = sqlite3.connect("aihost.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


######## Initialize DataBase ###########
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # create Table for api_keys
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL ,
        hash_key TEXT NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)

    # create table for usage_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY,
            api_key_id INTEGER NOT NULL,
            status_code INTEGER NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            latency_ms  REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
        );
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

    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, name FROM api_keys WHERE hash_key = ? AND is_active = 1""",
        (hash_key,),
    )
    a = cursor.fetchone()
    conn.close()
    return a


########### usages_logs #################
def log_usage(
    api_key_id, status_code, prompt_tokens, completion_tokens, total_tokens, latency_ms
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """ INSERT INTO usage_logs(
        api_key_id,
        status_code, 
        prompt_tokens, 
        completion_tokens, 
        total_tokens, 
        latency_ms)
        VALUES(?, ?, ?, ?, ?, ?)
        """,
        (
            api_key_id,
            status_code,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            latency_ms,
        ),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
