from db.db_helper import get_db_connection

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