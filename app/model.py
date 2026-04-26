# app/model.py
import os
import mlflow
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

def load_model():
    # load local
    #model = mlflow.sklearn.load_model("registered_model")
    
    mlclient = MLClient(
        DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_WORKSPACE_NAME"]
    )
    mlflow.set_tracking_uri(
        mlclient.workspaces.get(mlclient.workspace_name).mlflow_tracking_uri
    )
    model = mlflow.sklearn.load_model("models:/ChicagoParkingTickets_model/latest")

    return model 
