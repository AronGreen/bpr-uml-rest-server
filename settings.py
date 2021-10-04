import os
import json
from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DB = os.environ['MONGO_DB']
PORT = int(os.environ['PORT'])


def ensure_firebase_config():
    conf = {
    "type": os.environ['FB_CONF_TYPE'],
    "project_id": os.environ['FB_CONF_PROJECT_ID'],
    "private_key_id":  os.environ['FB_CONF_PRIVATE_KEY_ID'],
    "private_key": os.environ['FB_CONF_PRIVATE_KEY'],
    "client_email":  os.environ['FB_CONF_CLIENT_EMAIL'],
    "client_id": os.environ['FB_CONF_CLIENT_ID'],
    "auth_uri":  os.environ['FB_CONF_AUTH_URI'],
    "token_uri":  os.environ['FB_CONF_TOKEN_URI'],
    "auth_provider_x509_cert_url": os.environ['FB_CONF_AUTH_URI_PROVIDER_X509_CERT_URL'],
    "client_x509_cert_url": os.environ['FB_CONF_CLIENT_X509_CERT_URL']
    }

    # file_name = "bpr-uml-firebase-adminsdk-vjv02-6dff100a94.json"
    # file_name = "bpr-uml-firebase-adminsdk-vjv02-6dff100a94.json"
    # root_dir = os.path.dirname(os.path.abspath(__file__)) 
    # file_path = os.path.join(root_dir, "bpr-uml-firebase-adminsdk-vjv02-6dff100a94.json")
    file = open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], "w")       
    file.write(json.dumps(conf))  
    file.close()