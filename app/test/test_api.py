import os
import logging
from fastapi.testclient import TestClient
from app.server import app
from app.app.config.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

client = TestClient(app, base_url="http://testserver/api")
config = Config()

def test_session_without_files():
    session = "123"

    response = client.post(
        f'/chat_completion/',
        params={"file_id": session, "question": "What is the capital of France? Answer with the name only."}
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/event-stream; charset=utf-8'
    assert "Paris" in response.text

def test_session_with_files():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'sample-1.pdf'), 'rb') as file:
        response = client.post(f'/upload/', files={"file": file})
        print(response)

    assert response.status_code == 200
    
    id = response.json()['file_id']
    response_get_file = client.get(f"/files?file_id={id}")
    assert response_get_file.status_code == 200
    # check if a file exists in the server
    check_file_exists_in_server(id)

    assert clean_up(id)

def test_api_flush():
    response = client.delete('/flush')
    assert response.status_code != 200 # should not authorize

def get_parent_dir() -> str:
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    return parent_dir

def check_file_exists_in_server(id: str, name=None):
    data_dir = config.DATAFILES
    if name == None:
        file_path = os.path.join(data_dir, f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, f'{id}_{name}')
    print(file_path)
    assert os.path.exists(file_path)

def clean_up(id: str, name=None):
    data_dir = config.DATAFILES
    if name == None:
        file_path = os.path.join(data_dir, 'files', f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, 'files', f'{id}_{name}')

    # os.remove(file_path)
    return not os.path.exists(file_path)
