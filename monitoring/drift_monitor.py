from evidently.report import Report 
from evidently.metric_preset import DataDriftPreset 
from azure.storage.blob import BlobServiceClient 
import pandas as pd
import os
import json 

blob_service = BlobServiceClient(
    account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net",
    credential=os.environ["AZURE_STORAGE_SAS_TOKEN_LOGS"]
)

container = blob_service.get_container_client("predictions-log")

records = []
for f in container.list_blob_names():
    data = container.download_blob(f).readall() 
    records.extend(json.loads(data)["input"])
logged_df = pd.DataFrame(records)

training_df = pd.read_csv("pipeline/data/org/ChicagoParkingTickets.csv").sample(n=100000, random_state=42)
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=training_df, current_data=logged_df)
report.save_html("drift_report.html")