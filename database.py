import sqlite3

DB_NAME = "agenda.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_eventos():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # permite acceder por nombre de columna
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY fecha, hora")
    rows = c.fetchall()
    eventos = [dict(row) for row in rows]
    conn.close()
    return eventos

def add_evento(titulo, descripcion, fecha, hora):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO eventos (titulo, descripcion, fecha, hora) VALUES (?, ?, ?, ?)",
              (titulo, descripcion, fecha, hora))
    conn.commit()
    conn.close()

def get_evento(id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM eventos WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_evento(id, titulo, descripcion, fecha, hora):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE eventos 
        SET titulo=?, descripcion=?, fecha=?, hora=?
        WHERE id=?
    """, (titulo, descripcion, fecha, hora, id))
    conn.commit()
    conn.close()

def delete_evento(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eventos WHERE id=?", (id,))
    conn.commit()
    conn.close()
