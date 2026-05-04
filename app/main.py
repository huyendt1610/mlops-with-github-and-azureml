from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordRequestForm
import pandas as pd 
import io
import os 
from auth import create_token, verify_token

from logger import get_logger
from storage import log_prediction
from model import load_model

from prometheus_fastapi_instrumentator import Instrumentator
from metrics import PREDICTION_COUNT, PREDICTION_ROWS

app = FastAPI(title="Chicago Ticket Payment Prediction") 
model = load_model()
logger = get_logger("app")

# generate endpoint /metrics (request count, latency, ...)
Instrumentator().instrument(app).expose(app)

API_KEY = os.environ.get("API_KEY", '')
api_key_header = APIKeyHeader(name="X-API-Key")
def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.get("/")
def root():
    return {"status": "ok"}

# @app.get("/token")
# def login(form: OAuth2PasswordRequestForm = Depends()):
#     if form.username != os.environ["APP_USERNAME"] or form.password != os.environ["APP_PASSWORD"]: 
#         raise HTTPException(status_code=401, detail="Wrong credentials")
#     return {
#         "access_token": create_token({"sub": form.username}) 
#     }

@app.post("/predict")
async def predict(file: UploadFile = File(...), _: str = Security(verify_api_key)): # Depends(verify_token)
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
    
    contents = await file.read() 

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    predictions = model.predict(df).tolist()
    probs = model.predict_proba(df) 

    # for Data Drift
    log_prediction(df, predictions) 

    # for logging 
    logger.info("prediction_made", extra={
        "extra":{
            "rows": len(predictions), 
            "filename": file.filename
        }
    })

    # prometheus metrics
    PREDICTION_ROWS.observe(len(predictions)) 
    for label in predictions: 
        PREDICTION_COUNT.labels(label=str(label)).inc() 

    return {
        "total_rows": len(predictions),
        "predictions":[
            {
                "row": i, 
                "label": int(predictions[i]),
                "probability":{"0":probs[i][0], "1": probs[i][1]}
            }
            for i in range(len(predictions))
        ]
    }
    