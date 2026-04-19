import argparse
from pathlib import Path
from uuid import UUID 
from datetime import datetime
import os 
import pandas as pd 
import numpy as np 
import json 

from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.impute import SimpleImputer 
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler 
from sklearn.base import clone 
from sklearn.compose import make_column_transformer, make_column_selector
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score, classification_report

import mlflow
import mlflow.sklearn  

import utils 

# mlflow.set_experiment("local experiment ")
# mlflow.set_tracking_uri("http://localhost:5000")
# mlflow.set_tracking_uri("azureml://norwayeast.api.azureml.ms/mlflow/v1.0/subscriptions/cc71d3fb-a729-46cd-83e0-b6194219d1f1/resourceGroups/hd052437-rg/providers/Microsoft.MachineLearningServices/workspaces/gasoAML2") # http://127.0.0.1:5000

def main(args): 
   train_df = utils.build_df_from_folder(args.train_data)
   test_df = utils.build_df_from_folder(args.test_data)

   X_train, y_train = process_data(train_df)
   X_test, y_test = process_data(test_df)

   # train model 
   params = {
       'max_leaf_nodes': args.max_leaf_nodes, 
       'min_samples_leaf': args.min_samples_leaf, 
       'max_depth': 1, # args.max_depth, 
       'learning_rate': args.learning_rate, 
       'n_estimators': 1, #args.n_estimators, 
       'validation_fraction': 0.1, 
       'random_state': 11,
       'subsample': 0.1 # only get 20% of data for each tree
   }

   model, results = train_model(params, X_train, X_test, y_train, y_test) 

   print('Saving model...')
   mlflow.sklearn.save_model( # mlflow.pytorch, mlflow.tensorflow
       model, 
       args.model_output
    )

   print('Saving evaluation results')
   with open(Path(args.test_report)/'results.json', 'w') as file: 
       json.dump(results, file)

def train_model(params, X_train, X_test, y_train, y_test):
    num_pl = make_pipeline(
        SimpleImputer(strategy='median'),
        MinMaxScaler()
    )
    cat_pl = make_pipeline(
        SimpleImputer(strategy='most_frequent'),
        OneHotEncoder(sparse_output=False)
    )
    column_transformer = make_column_transformer(
        (num_pl, make_column_selector(dtype_include='number')), # dtype_exclude=['category']
        (cat_pl, make_column_selector(dtype_include=['category']))
    )

    # selector = make_column_selector(dtype_include='number')
    # columns = selector(X_train)
   

    clf = GradientBoostingClassifier(**params) 
    model = make_pipeline(column_transformer, clf)
    model = model.fit(X_train, y_train)
    y_preds = model.predict(X_test)

    report = classification_report(y_test, y_preds, output_dict=True)

    # accuracy = accuracy_score(y_test, y_preds)
    # f1 = f1_score(y_test, y_preds) 
    # f1_micro = f1_score(y_test, y_preds, average='micro') 
    # f1_macro = f1_score(y_test, y_preds, average='macro') 
    # precision = precision_score(y_test, y_preds)
    # recall = recall_score(y_test, y_preds)
    roc_auc = roc_auc_score(y_test, y_preds)

    print(report)
    results = {
        'accuracy': report['accuracy'], 
        'f1': report['1']['f1-score'],
        'f1_macro': report['macro avg']['f1-score'], 
        'precision': report['1']['precision'], 
        'recall': report['1']['recall'], 
        'roc_auc': roc_auc
    }

    mlflow.log_metrics(results)

    # mlflow.log_metric("accuracy", float(accuracy))
    # mlflow.log_metric("f1", float(f1))
    # mlflow.log_metric("f1_micro", float(f1_micro))
    # mlflow.log_metric("f1_macro", float(f1_macro))
    # mlflow.log_metric("precision", float(precision))
    # mlflow.log_metric("recall", float(recall))
    # mlflow.log_metric("roc_auc", float(roc_auc))

    return model, results

def process_data(df: pd.DataFrame): 
    label_column = "PaymentIsOutstanding"
    df = df[~df[label_column].isnull()]

    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist() 
    
    # remove label column from list
    if label_column in numerical_cols: 
        numerical_cols.remove(label_column)

    if label_column in categorical_cols: 
        categorical_cols.remove(label_column)

    # dtype
    for col in numerical_cols: 
        df[col] = df[col].astype('float64')

    for col in categorical_cols: 
        df[col] = df[col].astype('category')

    X = df.drop(columns=[label_column])
    y = df[label_column]

    return X, y

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", type=str, help="Path for prepared train data")
    parser.add_argument("--test_data", type=str, help="Path for prepared test data")
    parser.add_argument("--max_leaf_nodes", type=int)
    parser.add_argument("--min_samples_leaf", type=int)
    parser.add_argument("--max_depth", type=int)
    parser.add_argument("--learning_rate", type=float)
    parser.add_argument("--n_estimators", type=int)
    parser.add_argument("--model_output", type=str, help="Path of model_output")
    parser.add_argument("--test_report", type=str, help="Path of test_report")

    args = parser.parse_args() 
    return args

if __name__ == "__main__": 
    with mlflow.start_run():
        args = parse_args()
        main(args)
    print("Done!")
