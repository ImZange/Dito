import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
# 1. Importar load_dotenv
from dotenv import load_dotenv

# 2. Cargar las variables del archivo .env al inicio
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
            # 3. En lugar de leer un archivo físico, creamos un diccionario
            # con la estructura que la API espera, usando las variables de entorno.
            client_config = {
                "installed": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            # 4. Cambiamos 'from_client_secrets_file' por 'from_client_config'
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds)
        results = service.courses().list(pageSize=10).execute()
        courses = results.get('courses', [])

        lista_procesada = []
        if not courses:
            return [("Sin cursos", "No se encontraron cursos activos", "")]
        else:
            for course in courses:
                lista_procesada.append((course['name'], "Curso detectado", "Activo"))
            return lista_procesada

    except Exception as error:
        print(f"Ocurrió un error con la API de Google: {error}")
        raise error

def cerrar_sesion():
    if os.path.exists('token.json'):
        os.remove('token.json')
        return True
    return False