import sqlite3

DB_FILE = "college_data.db"

# ------------------ CHAT ------------------
def save_chat(user_id, role, message):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("INSERT INTO chat_history (user_id, role, message) VALUES (?,?,?)",
                (user_id, role, message))
    conn.commit()
    conn.close()

def load_chat_history(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("SELECT role, message FROM chat_history WHERE user_id=? ORDER BY id", (user_id,))
    data = cur.fetchall()
    conn.close()
    return data

# ------------------ USERS ------------------
def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mobile TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'student',
            course TEXT,
            year TEXT
        )
    """)
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    conn.close()
    return data

def update_user(user_id, name, mobile, course, year):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=?, mobile=?, course=?, year=? WHERE id=?",
                (name, mobile, course, year, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ------------------ DOCUMENTS / NOTICES ------------------
def get_all_documents():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    """)
    cur.execute("SELECT * FROM documents")
    data = cur.fetchall()
    conn.close()
    return data

def add_document(title, description):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO documents (title, description) VALUES (?,?)",
                (title, description))
    conn.commit()
    conn.close()

def update_document(doc_id, title, description):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE documents SET title=?, description=? WHERE id=?",
                (title, description, doc_id))
    conn.commit()
    conn.close()

def delete_document(doc_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()

# ------------------ LOAD KNOWLEDGE FOR AI ------------------
def load_knowledge():
    """
    Returns all documents and notifications as a list of dicts
    [{'title': ..., 'description': ...}, ...]
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Ensure tables exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    """)
    knowledge = []

    cur.execute("SELECT title, description FROM documents")
    for row in cur.fetchall():
        knowledge.append({"title": row[0], "description": row[1]})

    cur.execute("SELECT title, description FROM notifications")
    for row in cur.fetchall():
        knowledge.append({"title": row[0], "description": row[1]})

    conn.close()
    return knowledge
