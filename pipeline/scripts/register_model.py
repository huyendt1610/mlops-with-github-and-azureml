import mlflow
from mlflow.tracking import MlflowClient
import argparse
import json
from pathlib import Path
import os

print("Register model...")

with mlflow.start_run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, help="Path to trained model")
    parser.add_argument('--test_report', type=str, help="Path to model's test report")
    args = parser.parse_args()

    print('Loading model...')
    model = mlflow.sklearn.load_model(Path(args.model))

    print('Loading results...')
    fname = 'results.json'
    with open(Path(args.test_report) / fname, 'r') as f:
        results = json.load(f)

    print('Saving models locally...')
    root_model_path="registered_model"
    os.makedirs(root_model_path, exist_ok=True)
    mlflow.sklearn.save_model(model, root_model_path)

    print('Registering the model...')
    registered_model_name = "ChicagoParkingTickets_model"

    mlflow.set_tags(results) # tags on the run 
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name=registered_model_name,
        conda_env=str(Path(__file__).parent / "conda.yaml")
    )

print('Done!')
