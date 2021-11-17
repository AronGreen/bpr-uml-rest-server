import requests
import pytest

from bpr_data.models.user import User
from bpr_data.repository import Repository, Collection

import endpoint_test_util as util
import settings

repo = Repository.get_instance(
    protocol=settings.MONGO_PROTOCOL,
    default_db=settings.MONGO_DEFAULT_DB,
    pw=settings.MONGO_PW,
    host=settings.MONGO_HOST,
    user=settings.MONGO_USER)

created_resources = []
port_no = str(settings.APP_PORT)
port_no = str(5000)
base_url = "http://" + settings.APP_HOST + ":" + port_no + "/users"


@pytest.fixture(autouse=True)
def before_test():
    global token
    token = util.get_default_token_fixture()
    yield
    util.cleanup_fixture(created_resources)
    created_resources.clear()


def test_add_user():
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    assert settings.SMTP_EMAIL_ADDRESS == user.email
    created_resources.append({Collection.USER: user._id})


def test_add_user_a_second_time():
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    response = requests.post(url=base_url, headers={"Authorization": token})
    assert response.status_code == 200
    user = User.from_json(response.content.decode())
    assert settings.SMTP_EMAIL_ADDRESS == user.email
    created_resources.append({Collection.USER: user._id})
