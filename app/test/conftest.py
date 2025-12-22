import os

def get_parent_dir() -> str:
    """Get the parent directory of the current test directory"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    return parent_dir

def check_file_exists_in_server(id: str, name=None):
    """Check if a file exists in the server's data directory"""
    parent_dir = get_parent_dir() # path to ./app
    # Path to the other directory
    data_dir = os.path.join(parent_dir, 'data')
    if name == None:
        file_path = os.path.join(data_dir, 'files', f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, 'files', f'{id}_{name}')
    print(file_path)
    assert os.path.exists(file_path)

def clean_up(id: str, name=None):
    """Clean up a file from the server's data directory"""
    parent_dir = get_parent_dir()
    data_dir = os.path.join(parent_dir, 'data')
    if name == None:
        file_path = os.path.join(data_dir, 'files', f'{id}_sample-1.pdf')
    else:
        file_path = os.path.join(data_dir, 'files', f'{id}_{name}')

    # os.remove(file_path)
    return not os.path.exists(file_path)
