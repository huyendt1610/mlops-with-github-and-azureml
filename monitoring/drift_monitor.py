from evidently import Report
from evidently.presets import DataDriftPreset
from azure.storage.blob import BlobServiceClient 
import pandas as pd
import os
import json 

blob_service = BlobServiceClient(
    account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net",
    credential=os.environ["AZURE_STORAGE_KEY"]
)

container = blob_service.get_container_client("predictions-log")

records = []
for f in container.list_blob_names():
    data = container.download_blob(f).readall() 
    records.extend(json.loads(data)["input"])
logged_df = pd.DataFrame(records)

training_df = pd.read_csv("pipeline/data/org/ChicagoParkingTickets.csv").sample(n=100000, random_state=42)
report = Report([DataDriftPreset()])

common_cols = training_df.columns.intersection(logged_df.columns).tolist()

result = report.run(reference_data=training_df[common_cols], current_data=logged_df[common_cols])
os.makedirs("outputs", exist_ok=True)
result.save_html("outputs/drift_report.html")