import sqlite3
from db.db_helper import init_db, get_db_connection  # Actualizar la importación

def list_activities(limit=10):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM activity ORDER BY start_time DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    activities = list_activities()
    for activity in activities:
        print(f"ID: {activity[0]}, Start Time: {activity[1]}, End Time: {activity[2]}, Image Path: {activity[3]}")
