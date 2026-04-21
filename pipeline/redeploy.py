from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment

client = MLClient.from_config(DefaultAzureCredential())

def buildEnv():
    env_name = "aml-scikit-learn"
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

def main():
    buildEnv()

main()