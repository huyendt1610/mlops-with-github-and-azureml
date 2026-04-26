from fastapi import FastAPI, UploadFile, File, HTTPException
import mlflow
import pandas as pd 
import io
import os 
from datetime import datetime, timezone
import json 

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.storage.blob import BlobServiceClient

app = FastAPI(
    title="Chicago Ticket Payment Prediction"
) 
# load local
model = mlflow.sklearn.load_model("registered_model")

# load from aml registry 
# mlclient = MLClient(
#     DefaultAzureCredential(),
#     subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
#     resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
#     workspace_name=os.environ["AZURE_WORKSPACE_NAME"]
# ) 
# mlflow.set_tracking_uri(mlclient.workspaces.get(mlclient.workspace_name).mlflow_tracking_uri)
# model = mlflow.sklearn.load_model(model_uri="models:/ChicagoParkingTickets_model/latest")

def log_prediction(input_df, predictions): 
    blob_service = BlobServiceClient(
        account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net",
        credential=os.environ["AZURE_STORAGE_SAS_TOKEN_LOGS"]
    )
    container = blob_service.get_container_client("predictions-log")

    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(), 
        "input": input_df.to_dict(orient="records"),
        "predictions": predictions
    }

    blob_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.json"
    container.upload_blob(blob_name, json.dumps(log))

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
    
    contents = await file.read() 
   
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    # print(model)
    predictions = model.predict(df).tolist()
    log_prediction(df, predictions)
    # print(predictions)
    probs = model.predict_proba(df) 
    # print(probs)

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
    