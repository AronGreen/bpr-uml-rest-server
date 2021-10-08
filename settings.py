import os
import json
from dotenv import load_dotenv

load_dotenv()


APP_PORT = int(os.environ['APP_PORT'])

MONGO_PROTOCOL = os.environ['MONGO_PROTOCOL']
MONGO_USER = os.environ['MONGO_USER']
MONGO_PW = os.environ['MONGO_PW']
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_DEFAULT_DB = os.environ['MONGO_DEFAULT_DB']

def ensure_firebase_config():
    conf = {
        "type": os.environ['FB_CONF_TYPE'],
        "project_id": os.environ['FB_CONF_PROJECT_ID'],
        "private_key_id":  os.environ['FB_CONF_PRIVATE_KEY_ID'],
        "private_key": os.environ['FB_CONF_PRIVATE_KEY'].replace("\\n", "\n"),
        "client_email":  os.environ['FB_CONF_CLIENT_EMAIL'],
        "client_id": os.environ['FB_CONF_CLIENT_ID'],
        "auth_uri":  os.environ['FB_CONF_AUTH_URI'],
        "token_uri":  os.environ['FB_CONF_TOKEN_URI'],
        "auth_provider_x509_cert_url": os.environ['FB_CONF_AUTH_URI_PROVIDER_X509_CERT_URL'],
        "client_x509_cert_url": os.environ['FB_CONF_CLIENT_X509_CERT_URL']
    }
    file = open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], "w")       
    file.write(json.dumps(conf))  
    file.close()