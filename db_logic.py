import sqlite3

DB_NAME = "gestion_local.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Tabla para Classroom
        cursor.execute('''CREATE TABLE IF NOT EXISTS tareas_locales 
                          (id_tarea TEXT PRIMARY KEY, estado TEXT NOT NULL)''')
        # Tabla para tareas manuales
        cursor.execute('''CREATE TABLE IF NOT EXISTS tareas_manuales 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, materia TEXT, fecha TEXT, estado TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error DB: {e}")

def guardar_tarea_manual(titulo, materia, fecha, estado='pendiente'):
    """Recibe la fecha capturada en la interfaz y la guarda en SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tareas_manuales (titulo, materia, fecha, estado) 
            VALUES (?, ?, ?, ?)
        ''', (titulo, materia, fecha, estado))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al guardar manual: {e}")

def obtener_tareas_manuales():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, materia, fecha, id FROM tareas_manuales WHERE estado='pendiente'")
    res = cursor.fetchall()
    conn.close()
    return res

def marcar_manual_completada(t_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas_manuales SET estado='completado' WHERE id=?", (t_id,))
    conn.commit()
    conn.close()

def obtener_estados_locales():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id_tarea, estado FROM tareas_locales')
    res = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return res

def guardar_estado_local(id_tarea, estado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tareas_locales (id_tarea, estado) VALUES (?, ?)", (id_tarea, estado))
    conn.commit()
    conn.close()