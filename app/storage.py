# app/storage.py
import os
import json
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient

blob_service = BlobServiceClient(
    account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net",
    credential=os.environ['AZURE_STORAGE_ACCOUNT_KEY']
)
container = blob_service.get_container_client("predictions-log")

def log_prediction(input_df, predictions):
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": input_df.to_dict(orient="records"),
        "predictions": predictions
    }
    blob_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.json"
    container.upload_blob(blob_name, json.dumps(log))
