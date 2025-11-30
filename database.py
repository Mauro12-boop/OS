import sqlite3

DB_PATH = "resort.db"  # SQLite file name


def init_db(db_path: str = DB_PATH):
    """
    Create the SQLite database and the activities table if they don't exist.
    We only store what is already logged in Client.log_activity.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # One simple table: all activities from all clients
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            amenity TEXT,
            action TEXT,
            success INTEGER,
            info TEXT
        );
    """)

    conn.commit()
    conn.close()


def save_all_histories(clients, db_path: str = DB_PATH):
    """
    After the simulation ends, call this once.
    It will insert all logged activities for all clients.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO activities (client_id, amenity, action, success, info)
        VALUES (?, ?, ?, ?, ?);
    """

    for client in clients:
        for activity in client.history["activities"]:
            cur.execute(
                insert_sql,
                (
                    client.id,
                    activity["amenity"],
                    activity["action"],
                    activity["success"],
                    activity["info"],
                )
            )

    conn.commit()
    conn.close()
