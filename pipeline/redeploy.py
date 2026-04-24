from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment, CodeConfiguration
from pathlib import Path
import yaml
import scripts.utils

client = MLClient.from_config(DefaultAzureCredential())

def buildEnv():
    env_name = "aml-scikit-learn"
    conda_env = Path(__file__).parent/"scripts"/"conda.yaml"
    scikit_version = scripts.utils.get_package_version(conda_env, "scikit-learn")
    environment= Environment(
        name=env_name,
        description=env_name,
        tags={"scikit-learn": scikit_version},
        conda_file=conda_env,
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )  
    client.environments.create_or_update(environment)
    environment= client.environments.get(name=env_name, label="latest")

    print(f"Environment {env_name} created!")

def rebuildOnlineDeployment():
    deployment = client.online_deployments.get(endpoint_name="online-ticket-enpoint2", name="chicagoparkingtickets-model-6") 
    deployment.code_configuration = CodeConfiguration(code="pipeline/scripts", scoring_script="score_model_online.py")
    client.online_deployments.begin_create_or_update(deployment)

def buildModel():
    pass 

def main():
    rebuildOnlineDeployment()

main()