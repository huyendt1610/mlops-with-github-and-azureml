import sys 
import os 
import timeit
from datetime import datetime
import numpy as np 
import pandas as pd
import urllib
from urllib.parse import urlencode

from azure.ai.ml import MLClient, Input, Output  
from azure.ai.ml.entities import Workspace, AmlCompute 
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, AzureCliCredential
from azure.ai.ml.dsl import pipeline # Domain-Specific Language
from azure.ai.ml import load_component
from azure.ai.ml.constants import AssetTypes

from azure.ai.ml.sweep import (
    Choice, 
    Uniform
)
# workspace_name = ""
cluster_name = "demo-cluster"

ml_client = MLClient.from_config(AzureCliCredential())
# ws = ml_client.workspaces.get(workspace_name)

try:
    cpu_cluster = ml_client.compute.get(cluster_name)

    print(f"you already have a cluster named {cluster_name}, so we will use it for training.")
except Exception as ex:
    print(f"creating a new cluster named {cluster_name} for training.")
    cpu_cluster = AmlCompute(
        name=cluster_name,
        type="amlcompute", # amlcompute: on-demand compute; virtualmachine: single VM compute, kubernetes: AKS cluster 
        size="Standard_DS11_v2", #Standard_DS3_v2
        min_instances=0, # when no job running, scale down to 0
        max_instances=1, # max number of nodes in the cluster, you can change it based on your need and budget
        idle_time_before_scale_down=120, # how many seconds will the node running after the job is done 
        tier="Dedicated" # Dedicated or LowPriority: cheaper but there is a chance of job termination 
    )

    print(f"AmlCompute with name {cluster_name} will be created")
    cpu_cluster = ml_client.compute.begin_create_or_update(cpu_cluster)

parent_dir = "./pipeline/config"

# the 3 first steps can be grouped into one 
replace_missing_values=load_component(source=os.path.join(parent_dir, "feature-replace-missing-values.yml"))
feature_engineering=load_component(source=os.path.join(parent_dir,"feature-engineering.yml"))
feature_selection=load_component(source=os.path.join(parent_dir,"feature-selection.yml"))
split_data=load_component(source=os.path.join(parent_dir, "split-data.yml"))
train_model=load_component(source=os.path.join(parent_dir, "train-model.yml"))
register_model=load_component(source=os.path.join(parent_dir,"register-model.yml"))


@pipeline(name="training_pipeline",description="Build a training pipeline")
def build_pipeline(raw_data):
    # outputs is configed in yml => AML will create if it is not set properly
    # --output_data: managed default by AML and value is stored in step_replace_missing_value.outputs.output_data
    #  Azure ML runtime will create folder in blob storage and mount that folder into compute node (container)
    # compute node write outputs to that mounted folder 
    # then AML will sync that folder into cloud storage
    step_replace_missing_value=replace_missing_values(input_data=raw_data) 
    step_feature_engineering=feature_engineering(input_data=step_replace_missing_value.outputs.output_data) 
    step_feature_selection=feature_selection(input_data=step_feature_engineering.outputs.output_data)
    step_split_data=split_data(input_data=step_feature_selection.outputs.output_data)

    train_model_data=train_model(train_data=step_split_data.outputs.output_data_train,
                                 test_data=step_split_data.outputs.output_data_test,
                                 max_leaf_nodes=128,
                                 min_samples_leaf=32,
                                 max_depth=2, # for testing only, 12
                                 learning_rate=0.1,
                                 n_estimators=100
                                )

    register_model(model=train_model_data.outputs.model_output, test_report=train_model_data.outputs.test_report)
    return {
        "model": train_model_data.outputs.model_output,
        "report": train_model_data.outputs.test_report
    }

def prepare_pipeline_job(cluster_name): 
    # must have a dataset already in place 
    cpt_dataset=ml_client.data.get(name="ticket_folder",version="1")
    raw_data=Input(type='uri_folder', path=cpt_dataset.path)
    pipeline_job = build_pipeline(raw_data)
    
    #set pipeline level compute 
    pipeline_job.settings.default_compute = cluster_name 

    # set pipeline level datastore 
    pipeline_job.settings.default_datastore = 'workspaceblobstore'
    #pipeline_job.settings.force_rerun = True  # commented to save computing 
    pipeline_job.display_name="train_pipeline"
    return pipeline_job

def main():
    prepared_job = prepare_pipeline_job(cluster_name)
    ml_client.jobs.create_or_update(prepared_job, experiment_name="aml_pipeline")  

main()