from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path

mock_model = MagicMock() 
mock_model.predict.return_value = [1, 0]
mock_model.predict_proba.return_value = [[0.3, 0.7],[0.8, 0.2]]

with patch("model.MLClient"), patch("model.mlflow", return_value=mock_model):
    from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_wrong_format():
    response = client.post("/predict", files={"file": ("text.txt", b"data", "text/plain")})
    assert response.status_code == 400

def test_predict_csv():
    path = Path(__file__).parent / "sample.csv"
    with patch("main.log_prediction"), open(path, "rb") as f:
        response = client.post("/predict", files={"file": f})
    assert response.status_code == 200
    assert "predictions" in response.json()