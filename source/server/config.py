from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
DRIVE_DIR = Path(os.getenv('HOMEDRIVE_PATH', BASE_DIR / 'drive')).resolve()
HOST = os.getenv('HOMEDRIVE_HOST', '0.0.0.0')
PORT = int(os.getenv('HOMEDRIVE_PORT', '8000'))
USERNAME = os.getenv('HOMEDRIVE_USER', 'admin')
PASSWORD = os.getenv('HOMEDRIVE_PASSWORD', 'change-me')
SECRET_KEY = os.getenv('HOMEDRIVE_SECRET', 'change-this-secret')
AUTH_DB = Path(os.getenv('HOMEDRIVE_AUTH_DB', BASE_DIR / 'server' / 'homedrive_auth.sqlite3'))
TEXT_EXTENSIONS = {'.txt','.md','.json','.csv','.py','.html','.css','.js'}
SPREADSHEET_EXTENSIONS = {'.csv','.xlsx','.xls'}

USER_FOLDERS = ['Documents','Images','Musique','Videos','Applications','Archives','Partages','Corbeille']
