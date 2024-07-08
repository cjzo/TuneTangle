import sqlite3

def init_db():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_songs (
            user_id TEXT PRIMARY KEY,
            song_ids TEXT,
            total_songs INT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
