# Utilidades para crear una base de datos SQLite, registrar actividad y obtener registros de actividad
import sqlite3
import os

DB_PATH = 'activity_log.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                image_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def log_activity(start_time, end_time, image_path):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO activity (start_time, end_time, image_path)
        VALUES (?, ?, ?)
    ''', (start_time, end_time, image_path))
    conn.commit()
    conn.close()

def get_activity_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM activity ORDER BY start_time DESC')
    rows = c.fetchall()
    conn.close()
    return rows