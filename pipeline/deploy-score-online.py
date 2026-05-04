from azure.ai.ml import (
    MLClient
)
from azure.core.exceptions import ResourceNotFoundError

from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import ( Environment, ManagedOnlineDeployment, ManagedOnlineEndpoint, CodeConfiguration) 

model_name = "ChicagoParkingTickets_model"
env_name = "aml-scikit-learn"
endpoint_name = "ticket-endpoint-online"
deployment_name = "ticket-deployment-online" 

client = MLClient.from_config(DefaultAzureCredential())

model = client.models.get(name=model_name, label="latest")
try: 
    environment = client.environments.get(name=env_name, version="15")
except ResourceNotFoundError:
    environment = Environment( 
        name=env_name, 
        version="15", 
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04:latest",
        conda_file="./scripts/conda.yaml"
    )

try:
    endpoint = client.online_endpoints.get(name=endpoint_name)
except ResourceNotFoundError:
    print(f"Endpoint {endpoint_name} does not exist. Creating the new endpoint...")
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name, 
        description="Online endpoint for ticket model", 
        auth_mode="key"
    )
    endpoint = client.online_endpoints.begin_create_or_update(endpoint).result()

try:
    deployment = client.online_deployments.get(name=deployment_name, endpoint_name=endpoint_name)
except ResourceNotFoundError:
    print(f"Deployment {deployment_name} does not exist. Creating the new deployment...")
    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        description="Online deployment for ticket model",
        endpoint_name=endpoint_name,
        model=model,
        environment=environment,
        instance_type="Standard_DS2_v2",
        instance_count=1,
        code_configuration= CodeConfiguration( 
            code="./scripts", scoring_script="score_model_online.py"
        ),
        retry_settings={"max_retries": 3, "timeout": 60}, 
        liveness_probe_settings={"initial_delay": 30, "period": 10, "failure_threshold": 3},
        readiness_probe_settings={"initial_delay": 30, "period": 10, "failure_threshold": 3}
        
    )
    deployment = client.online_deployments.begin_create_or_update(deployment).result()
    endpoint.defaults.deployment_name = deployment_name  
    endpoint.traffic = {deployment_name: 100} 
    endpoint = client.online_endpoints.begin_create_or_update(endpoint).result() 
