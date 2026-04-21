from azure.ai.ml import MLClient, Input, Output
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    AmlCompute,
    BatchEndpoint, ModelBatchDeployment, 
    CodeConfiguration, ModelBatchDeploymentSettings, BatchRetrySettings, 
    Data, Environment
 )
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction
import mlflow
import pandas as pd 
import mltable


cluster_name = "demo-cluster"

client = MLClient.from_config(DefaultAzureCredential())
# tracking_uri = client.workspaces.get().mlflow_tracking_uri
# mlflow.set_tracking_uri(tracking_uri)
# print(f"Connected to: {tracking_uri}")

# mlflow_client = mlflow.tracking.MlflowClient() 
# exp  = mlflow.get_experiment_by_name(name='current_ticket_exper')
# runs = mlflow.search_runs(experiment_ids=exp.experiment_id, output_format='list')
# last_run = runs[-1]
# print(last_run.info.run_id)

# data = ml_client.data.get(name='ticket', version='1')
# tbl = mltable.load(f"azureml:/{data.id}")
# df = tbl.to_pandas_dataframe()

# 1. cluster 
try: 
    cluster = client.compute.get(name=cluster_name)
    print(f"Cluster {cluster_name} exists. We'll use it!")
except Exception:
    print(f"Cluster {cluster_name} does not exist. Creating the new cluster...")
    cluster = AmlCompute(
        name=cluster_name, 
        type="amlcompute",
        size="Standard_DS11_v2",
        min_instances=0,
        max_instances=1,
        idle_time_before_scale_down=180,
        tier="Dedicated"
    )
    cluster = client.compute.begin_create_or_update(cluster)

# 2. endpoint 
endpoint_name = "ticket-endpoint"
try: 
    endpoint = client.batch_endpoints.get(name=endpoint_name)
    print(f"Endpoint {endpoint_name} exists. We'll use it") 
except Exception: 
    print(f"Creating a new endpoint: {endpoint_name}")
    endpoint = BatchEndpoint(
        name=endpoint_name, 
        description="Endpoint for ticket model"
    )
    client.batch_endpoints.begin_create_or_update(endpoint).result() 
    endpoint = client.batch_endpoints.get(name=endpoint_name)
    print(f"Endpoint created: {endpoint.name}")

# 3. model 
model_name = "ChicagoParkingTickets_model"
model = client.models.get(name=model_name, label="latest")
print("Retrieved model")

# 4. environment  
# env_name =  "sklearn-1.5"
# environment = client.environments.get(name=env_name, version=43)
# print("Retrived environment")

# AzureML-framework-fwVersion-OS-pythonVersion-computeTarget(Cpu/gpu)
#environment=client.environments.get(name="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu", version="33")
# envs = client.environments.list() 
# for e in envs: 
#     print(e.name, e.version)

# print("Retrieved environment")
env_name = "aml-scikit-learn"
    
try:
    environment= client.environments.get(name=env_name, label="latest")
    print(f"Environment {env_name} exists. We'll use it!") 
except Exception:
    print(f"Creating environment named: {env_name}...")
    environment= Environment(
        name=env_name,
        description=env_name,
        tags={"scikit-learn": "1.7.2"},
        conda_file="pipeline/environment/conda.yaml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )  
    client.environments.create_or_update(environment)
    environment= client.environments.get(name=env_name, label="latest")

    print(f"Environment {env_name} created!")

# 5. Deployment 
deploy_name ="cpt-batch-deployment"
try:
    deployment = client.batch_deployments.get(endpoint_name=endpoint.name, name=deploy_name)
    print(f"You have the deployment named: {deploy_name}. We'll use it")
except Exception:
    # environment=client.environments.get(name="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu", version="33") 
    deployment = ModelBatchDeployment(
        name=deploy_name,
        description="Batch deployment of chicago tiket payment status",
        environment=environment,
        compute=cluster_name,
        endpoint_name=endpoint.name,
        model=model, 
        code_configuration=CodeConfiguration(code="pipeline/scripts", scoring_script="score_model.py"),
        settings=ModelBatchDeploymentSettings(
            instance_count=2, 
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchDeploymentOutputAction.APPEND_ROW,
            output_file_name="prediction.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=300),
            logging_level="info"
        )
    )

    client.batch_deployments.begin_create_or_update(deployment=deployment).result() 
    print("Deployment created!")

    endpoint.defaults.deployment_name = deploy_name 
    client.batch_endpoints.begin_create_or_update(endpoint).result() 
    print("Updated default deployment to the endpoint")


data_path="pipeline/data/predict"
dataset_name = "ticket-unlabeled"
try:
    predict_data = client.data.get(name=dataset_name, label="latest")
    print(f"You already have the dataset {dataset_name}. We'll use it!")
except Exception:
    predict_data = Data(
        name=dataset_name,
        description="Data for ticket prediction",
        path=data_path,
        type=AssetTypes.URI_FOLDER
    )
    client.data.create_or_update(predict_data)
    predict_data = client.data.get(name=dataset_name, label="latest")
    print("Data retrieved!")
 

job = client.batch_endpoints.invoke( # create job 
    endpoint_name=endpoint.name, 
    # deployment_name= # in case want to test with a non-default deployment 
    inputs={
        "input_data": Input(
            type=AssetTypes.URI_FOLDER,
            path=predict_data.path
        )
    }
)

# client.jobs.stream(job.name)

# client.jobs.download(
#     name=job.name, 
#     download_path="outputs/score-predict",
#     output_name="score"
# )