from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path
import numpy as np

mock_model = MagicMock()
mock_model.predict.return_value = np.array([1, 0])
mock_model.predict_proba.return_value = np.array([[0.3, 0.7], [0.8, 0.2]])

with patch("model.load_model", return_value=mock_model), \
     patch.dict("os.environ", {"API_KEY": "test-key"}):
    from main import app

client = TestClient(app)
AUTH = {"X-API-Key": "test-key"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_wrong_format():
    response = client.post("/predict", headers=AUTH, files={"file": ("text.txt", b"data", "text/plain")})
    assert response.status_code == 400

def test_predict_csv():
    path = Path(__file__).parent / "sample.csv"
    with patch("main.log_prediction"), open(path, "rb") as f:
        response = client.post("/predict", headers=AUTH, files={"file": f})
    assert response.status_code == 200
    assert "predictions" in response.json()