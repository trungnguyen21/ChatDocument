import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from google import genai

from app.server import app
from app.app.config import config
import httpx

client = TestClient(app)
keys = config.Config()

def test_llm_connection():
    # Test that the LLM client is properly connected
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents="Hi"
        )
        assert response.text
    except httpx.ConnectError as e:
        pytest.fail(f"LLM connection failed: {e}")

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Mock Redis for testing"""
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis.flushall.return_value = False
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.lrange.return_value = []
    mock_redis.exists.return_value = True
    mock_redis.keys.return_value = ["doc:test_id:1", "message_store:test_id:1"]
    
    # Mock Utils class
    mock_utils = MagicMock()
    mock_utils.get_session_history.return_value.messages = []
    monkeypatch.setattr("app.modules.utils.Utils.get_session_history", lambda x, y: mock_utils.get_session_history(x, y))
    
    # Patch the redis client in the app
    monkeypatch.setattr("app.app.redis_client", mock_redis)
    return mock_redis

@pytest.fixture(autouse=True)
def mock_file_operations(monkeypatch, tmp_path):
    """Mock file operations"""
    def mock_save_file(self, *args, **kwargs):
        return True
    
    def mock_get_file_by_id(self, file_id):
        return str(tmp_path / f"{file_id}.pdf")
    
    monkeypatch.setattr("app.modules.cache.Cache.save_file", mock_save_file)
    monkeypatch.setattr("app.modules.cache.Cache.get_file_by_id", mock_get_file_by_id)
    monkeypatch.setattr("app.modules.cache.Cache.save_file_map", mock_save_file)
    
    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("test content")
    return tmp_path

@pytest.fixture(autouse=True)
def mock_rag_chat(monkeypatch):
    """Mock RagChat operations"""
    async def mock_chat_completion(*args, **kwargs):
        class MockToken:
            def __init__(self, content):
                self.content = content
        yield MockToken("Test response")
    
    async def mock_output_generation(*args, **kwargs):
        yield "Test response"
    
    monkeypatch.setattr("app.modules.rag_chat.RagChat.chat_completion", mock_chat_completion)
    monkeypatch.setattr("app.modules.rag_chat.RagChat.output_generation", mock_output_generation)

@pytest.fixture
def test_file(mock_file_operations):
    """Fixture to handle file upload and cleanup"""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    with open(os.path.join(current_dir, 'sample-1.pdf'), 'rb') as file:
        response = client.post(
            "/api/upload/",
            files={"file": ("sample-1.pdf", file, "application/pdf")}
        )
    
    assert response.status_code == 200
    file_id = response.json()['file_id']
    
    yield file_id
    
    # Cleanup after test completes
    client.delete("/api/delete", params={"file_id": file_id})

def test_root():
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_chat():
    response = client.post(
        "/api/chat/",
        params={"question": "What is FastAPI?"}
    )
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/plain')

def test_db_health():
    response = client.get("/api/db-health")
    assert response.status_code == 200
    assert response.json() == {"message": "Database is healthy"}

@pytest.mark.parametrize(
    "file_content,expected_status",
    [
        ("test content", 200),
        ("", 200),  # Empty file should still upload
    ]
)
def test_file_upload(file_content, expected_status, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text(file_content)
    
    with open(test_file, 'rb') as file:
        response = client.post(
            "/api/upload/",
            files={"file": ("test.pdf", file, "application/pdf")}
        )
    
    assert response.status_code == expected_status
    assert "file_id" in response.json()
    assert isinstance(response.json()["file_id"], str)

def test_file_deletion(test_file, mock_redis):
    response = client.delete("/api/delete", params={"file_id": test_file})
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully."}
    
    # Verify Redis calls
    mock_redis.delete.assert_called()

def test_preprocessing_status():
    # Test valid task ID
    with patch('app.app.fetch_task_result') as mock_fetch:
        mock_fetch.return_value = {"status": "SUCCESS"}
        response = client.get("/api/preprocessing_status", params={"task_id": "valid_task"})
        assert response.status_code == 200
        assert response.json() == {"status": "SUCCESS"}
    
    # Test invalid task ID
    response = client.get("/api/preprocessing_status", params={"task_id": "invalid_task"})
    assert response.status_code == 404
    assert "Cannot find the specified task" in response.json()["detail"]

def test_session_without_files():
    response = client.post(
        "/api/chat_completion/",
        params={
            "file_id": "123",
            "question": "What is the capital of France? Answer with the name only."
        }
    )
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/event-stream')

@pytest.mark.asyncio
async def test_session_with_files(test_file, mock_file_operations):
    # Create a test file in the mock filesystem
    file_path = mock_file_operations / f"{test_file}.pdf"
    file_path.write_text("test content")

    # Test getting file info
    response_get_file = client.get("/api/files", params={"file_id": test_file})
    assert response_get_file.status_code == 200

@pytest.mark.asyncio
@patch('app.app.process_document')
async def test_model_activation(mock_process, test_file, mock_file_operations):
    # Mock celery task
    mock_process.delay.return_value.id = "test_task_id"
    
    # Create a test file in the mock filesystem
    file_path = mock_file_operations / f"{test_file}.pdf"
    file_path.write_text("test content")

    # Test model activation
    response = client.post(
        "/api/model_activation",
        json={"file_id": test_file}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["task_id"] == "test_task_id"

def test_api_chat_history():
    response = client.get(
        "/api/chat_history",
        params={"session_id": "123"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_chat_completion_without_context():
    response = client.post(
        "/api/chat_completion/",
        params={
            "file_id": "nonexistent_id",
            "question": "What is FastAPI?"
        }
    )
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/event-stream')

@pytest.mark.asyncio
async def test_chat_completion_with_context(test_file, mock_file_operations):
    # Setup mock cached file
    with patch('app.modules.cache.Cache.get_cached_file') as mock_cache:
        mock_cache.return_value = (MagicMock(), MagicMock())
        
        response = client.post(
            "/api/chat_completion/",
            params={
                "file_id": test_file,
                "question": "What is in the document?"
            }
        )
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('text/event-stream')

def test_error_handling():
    # Test files endpoint with invalid file_id
    response = client.get("/api/files", params={"file_id": "invalid_id"})
    assert response.status_code == 200  # Current behavior returns 200 even for invalid IDs

    # Test model activation with invalid file_id
    response = client.post(
        "/api/model_activation",
        json={"file_id": "invalid_id"}
    )
    assert response.status_code == 404

    # Test model activation with invalid schema
    response = client.post(
        "/api/model_activation",
        json={"invalid_field": "value"}  # Missing required file_id field
    )
    assert response.status_code == 422  # Pydantic validation error

    # Test model activation with empty body
    response = client.post("/api/model_activation", json={})
    assert response.status_code == 422

    # Test file deletion with invalid file_id
    with patch('app.modules.cache.Cache.delete_file', side_effect=Exception("File not found")):
        response = client.delete("/api/delete", params={"file_id": "invalid_id"})
        assert response.status_code == 500
        assert "Error in deleting file" in response.json()["detail"]
