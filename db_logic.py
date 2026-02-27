import sqlite3
import os

# Nombre del archivo de base de datos que se creará en tu carpeta
DB_NAME = "gestion_local.db"

def init_db():
    """Inicializa la base de datos y crea la tabla de estados si no existe."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # id_tarea guardará el ID único que nos da Google
        # estado guardará 'oculto' o 'completado'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas_locales (
                id_tarea TEXT PRIMARY KEY,
                estado TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Base de datos local SQLite: Conectada y lista.")
    except sqlite3.Error as e:
        print(f"Error crítico al inicializar SQLite: {e}")

def guardar_estado_local(id_tarea, estado):
    """Guarda o actualiza el estado de una tarea en el sistema local."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # INSERT OR REPLACE evita errores si intentas marcar la misma tarea dos veces
        cursor.execute('''
            INSERT OR REPLACE INTO tareas_locales (id_tarea, estado)
            VALUES (?, ?)
        ''', (id_tarea, estado))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al guardar estado en SQLite: {e}")

def obtener_estados_locales():
    """Devuelve un diccionario con todas las tareas ya gestionadas para filtrarlas."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id_tarea, estado FROM tareas_locales')
        # Retornamos un diccionario {id: estado} para búsqueda rápida en gui.py
        resultados = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return resultados
    except sqlite3.Error as e:
        print(f"Error al leer de SQLite: {e}")
        return {}