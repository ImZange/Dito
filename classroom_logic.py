import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me'
]

def obtener_tareas():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds)
        results = service.courses().list(pageSize=15).execute()
        courses = results.get('courses', [])

        todas_las_tareas_pendientes = []
        
        if not courses:
            return [("Sin cursos", "No se encontraron clases", "Info", "none")]

        for course in courses:
            c_id = course['id']
            c_name = course['name']
            
            # 1. Obtener detalles de tareas
            cw_results = service.courses().courseWork().list(courseId=c_id).execute()
            tasks_data = {t['id']: t for t in cw_results.get('courseWork', [])}
            
            if not tasks_data:
                continue

            # 2. Obtener tus entregas personales
            subs_results = service.courses().courseWork().studentSubmissions().list(
                courseId=c_id, courseWorkId='-', userId='me').execute()
            submissions = subs_results.get('studentSubmissions', [])

            for sub in submissions:
                # Filtrar solo estados pendientes
                if sub.get('state') in ['NEW', 'CREATED', 'RECLAIMED_BY_STUDENT']:
                    work_id = sub.get('courseWorkId')
                    task = tasks_data.get(work_id)
                    
                    if task:
                        titulo = task.get('title')
                        t_id = task.get('id') # Extraemos el ID para SQLite
                        due = task.get('dueDate')
                        
                        if due:
                            fecha = f"{due.get('day')}/{due.get('month')}/{due.get('year')}"
                        else:
                            fecha = "Sin fecha"
                        
                        # Retornamos la tupla de 4 elementos requerida por gui.py
                        todas_las_tareas_pendientes.append((titulo, c_name, fecha, t_id))
            
        # Nota: He eliminado el bucle 'for task in tasks' que causaba el error

        if not todas_las_tareas_pendientes:
            return [("¡Al día!", "No tienes tareas pendientes", "Genial", "none")]
            
        return todas_las_tareas_pendientes

    except Exception as error:
        print(f"Error en API Classroom: {error}")
        raise error

def cerrar_sesion():
    if os.path.exists('token.json'):
        os.remove('token.json')
        return True
    return False