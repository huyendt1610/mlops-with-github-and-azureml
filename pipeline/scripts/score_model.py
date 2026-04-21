import os
import mlflow
import glob
import pandas as pd 

def init():
    global model 
    
    print("Loading model")
    model_dir = os.environ["AZUREML_MODEL_DIR"] # /mnt/azureml/cr.../...d9e_score_model

    # AZUREML_MODEL_DIR points to the artifact root; the MLflow model is one level deeper
    mlmodel_files = glob.glob(os.path.join(model_dir, "**", "MLmodel"), recursive=True) # **: folder name like in artifacts: trained_models/
    model_path = os.path.dirname(mlmodel_files[0]) if mlmodel_files else model_dir
    print(f"Model path resolved to: {model_path}")
    model = mlflow.sklearn.load_model(model_path)

def run(mini_batch):
    print(f"run method start: {__file__}, run ({len(mini_batch)}) files")
    try:
        data = pd.concat(
            [pd.read_csv(fp) for fp in mini_batch],
            ignore_index=True  # reset index to avoid misalignment across files
        )
        print(f"Loaded data shape: {data.shape}, columns: {list(data.columns)}")

        pred = model.predict(data)
        return data.assign(PaymentIsOutstanding=pred)
    except Exception as e:
        print(f"ERROR in run(): {e}")
        raise