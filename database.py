import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utils import safe_json_loads
from contextlib import contextmanager

DB_NAME = 'allergie_tracker.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=(), fetch=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()

def create_table(table_name, schema):
    query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {schema}
        )
    '''
    execute_query(query)

def init_db():
    create_table('users', '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    ''')
    create_table('entries', '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        date TEXT NOT NULL,
        aliments TEXT NOT NULL,
        symptomes TEXT NOT NULL,
        FOREIGN KEY (user_email) REFERENCES users (email)
    ''')
    create_table('aliments', '''
        nom TEXT PRIMARY KEY
    ''')
    print("Database initialized successfully.")

def register_user(email, password, first_name, last_name):
    hashed_password = generate_password_hash(password)
    try:
        execute_query(
            'INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)', 
            (email, hashed_password, first_name, last_name)
        )
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists

def login_user(email, password):
    user = execute_query('SELECT * FROM users WHERE email = ?', (email,), fetch=True)
    if user and check_password_hash(user[0]['password'], password):
        return True
    return False

def get_aliments():
    aliments = execute_query("SELECT nom FROM aliments", fetch=True)
    return [row['nom'] for row in aliments]

def add_aliment(nom):
    execute_query("INSERT OR IGNORE INTO aliments (nom) VALUES (?)", (nom,))

def add_entry(user_email, date, aliments, symptomes_data):
    aliments_json = json.dumps(aliments)
    symptomes_json = json.dumps(symptomes_data)
    execute_query(
        "INSERT INTO entries (user_email, date, aliments, symptomes) VALUES (?, ?, ?, ?)", 
        (user_email, str(date), aliments_json, symptomes_json)
    )

def get_entries(user_email):
    entries = execute_query(
        "SELECT date, aliments, symptomes FROM entries WHERE user_email = ?", 
        (user_email,), 
        fetch=True
    )
    return [
        (
            datetime.strptime(row['date'], '%Y-%m-%d').date(),
            safe_json_loads(row['aliments']),
            safe_json_loads(row['symptomes'])
        ) 
        for row in entries
    ]

def clean_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, * FROM entries")
        rows = cursor.fetchall()
        for row in rows:
            rowid, _, _, date, aliments, symptomes = row
            try:
                json.loads(aliments)
                json.loads(symptomes)
            except json.JSONDecodeError:
                cursor.execute("DELETE FROM entries WHERE rowid = ?", (rowid,))
        conn.commit()
        
def update_entry(user_email, date, aliments, symptomes_data):
    aliments_json = json.dumps(aliments)
    symptomes_json = json.dumps(symptomes_data)
    execute_query(
        "UPDATE entries SET aliments = ?, symptomes = ? WHERE user_email = ? AND date = ?", 
        (aliments_json, symptomes_json, user_email, str(date))
    )

def delete_entry(user_email, date):
    execute_query(
        "DELETE FROM entries WHERE user_email = ? AND date = ?", 
        (user_email, str(date))
    )

# Call init_db() when this module is imported
init_db()