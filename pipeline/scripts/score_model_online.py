import mlflow
import os
import io
import glob
import pandas as pd

def init():
    global model

    model_dir = os.environ["AZUREML_MODEL_DIR"]
    mlmodel_files = glob.glob(os.path.join(model_dir, "**", "MLmodel"), recursive=True)
    model_path = os.path.dirname(mlmodel_files[0]) if mlmodel_files else model_dir

    model = mlflow.sklearn.load_model(model_path)

def run(raw_data):
    df = pd.read_csv(io.StringIO(raw_data))
    for col in df.select_dtypes(exclude=["number"]).columns:
        df[col] = df[col].astype("category")
    result = model.predict(df)
    return result.tolist()
