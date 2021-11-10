import endpoint_test_util as util
import requests
import settings
import pytest
from src.models.user import User
import src.repository as repo

created_resources = []
port_no = str(settings.APP_PORT)
port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/users"

@pytest.fixture(autouse=True)
def before_test():
    global token
    token = util.get_token()
    yield
    util.cleanup(created_resources)
    created_resources.clear()

def test_add_user():
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    assert settings.SMTP_EMAIL_ADDRESS == user.email
    created_resources.append({repo.Collection.USER: user._id})

def test_add_user_a_second_time():
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 400
    db_user = repo.find(repo.Collection.USER, firebaseId=user.firebaseId)
    assert len(db_user) == 1
    created_resources.append({repo.Collection.USER: user._id})