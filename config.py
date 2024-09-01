import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE = 'database.db'
OIDC_CLIENT_ID = os.getenv('OIDC_CLIENT_ID')
OIDC_CLIENT_SECRET = os.getenv('OIDC_CLIENT_SECRET')
OIDC_DISCOVERY_URL = os.getenv('OIDC_DISCOVERY_URL')
JOIN_FORM_URL = 'https://forms.gle/KwACC2wvx9xWKPD37'