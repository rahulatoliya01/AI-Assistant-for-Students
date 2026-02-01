import sqlite3

def login(mobile, password):
    conn = sqlite3.connect("college_data.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, role, course, year FROM users WHERE mobile=? AND password=?",
        (mobile, password)
    )
    user = cur.fetchone()
    conn.close()
    return user


def register_user(name, mobile, password, course, year):
    conn = sqlite3.connect("college_data.db")
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO users (name, mobile, password, role, course, year)
        VALUES (?, ?, ?, 'student', ?, ?)
        """, (name, mobile, password, course, year))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()
