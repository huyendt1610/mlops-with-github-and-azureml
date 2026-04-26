from fastapi.testclient import TestClient 
from main import app 
from pathlib import Path 

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200 
    assert response.json() == {"status": "ok"}

def test_predict_wrong_format():
    response = client.post("/predict", files={"file": ("text.txt", b"data", "text/plain")}) # create a txt file
    assert response.status_code == 400 

def test_predict_csv():
    path = Path(__file__).parent / "sample.csv"
    with open(path, "rb") as f:
        response = client.post("/predict", files={"file": f})
    assert response.status_code == 200 
    assert "predictions" in response.json()