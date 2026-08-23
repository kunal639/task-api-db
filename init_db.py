import sqlite3

DB_NAME = "tasks.db"


def init_db():
  with sqlite3.connect(DB_NAME) as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
      cursor.executemany(
          "INSERT INTO tasks (title, done) VALUES (?, ?)",
          [("study", 0), ("sleep", 1), ("exercise", 0)],
      )
      conn.commit()