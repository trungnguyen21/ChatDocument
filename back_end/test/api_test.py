import requests, os

url = 'http://localhost:8000/api' # ran on local server

def test_db_health():
    response = requests.get(url + '/db-health')
    assert response.status_code == 200
    assert response.json() == {"message": "Database is healthy!"}

def test_session_without_files():
    s = requests.Session()
    session = "123"

    with s.get(
        f'{url}/chat_completion/',
        stream=True,
        params={"session_id": session, "question": "What is the capital of France? Answer with the name only."},
    ) as response:
        assert response.status_code == 200
        assert response.headers['Transfer-Encoding'] == 'chunked'
        assert response.headers['Content-Type'] == 'text/event-stream; charset=utf-8'

def test_session_with_files():
    s = requests.Session()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'sample-1.pdf'), 'rb') as file:
        response = s.post(f'{url}/upload/', files={"file": file})
        print(response)

    assert response.status_code == 200
    assert response.json()['Result'] == 'OK'
    
    id = response.json()['file_id']
    response_get_file = s.get(f"{url}/files?file_id={id}")
    assert response_get_file.status_code == 200
    # check if a file exists in the server
    check_file_exists_in_server(id)

    # clean up after testing
    response_delete = s.delete(f"{url}/delete?file_id={id}")
    assert response_delete.status_code == 200
    assert clean_up(id)

def test_api_chat_history():
    s = requests.Session()
    session = '123'
    with s.get(
        f'{url}/chat_history/',
        params={"session_id": session},
    ) as response:
        assert response.status_code == 200

def test_api_flush():
    response = requests.delete(url + '/flush')
    assert response.status_code != 200 # should not authorize!

def get_parent_dir() -> str:
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    return parent_dir

def check_file_exists_in_server(id: str, name=None):
    parent_dir = get_parent_dir() # path to ./back_end
    # Path to the other directory
    data_dir = os.path.join(parent_dir, 'data')
    if name == None:
        file_path = os.path.join(data_dir, 'files', f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, 'files', f'{id}_{name}')
    print(file_path)
    assert os.path.exists(file_path)

def clean_up(id: str, name=None):
    parent_dir = get_parent_dir()
    data_dir = os.path.join(parent_dir, 'data')
    if name == None:
        file_path = os.path.join(data_dir, 'files', f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, 'files', f'{id}_{name}')

    # os.remove(file_path)
    return not os.path.exists(file_path)