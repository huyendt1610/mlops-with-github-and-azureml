import argparse
from pathlib import Path
import os 
import pandas as pd 
import pickle
import mlflow
import mlflow.sklearn 
import sys 
import timeit  
import numpy as np 
import utils

def main(args):
    print("Replacing missing values...")

    df = utils.build_df_from_folder(args.input_data)

    # replace missing value 
    df['Police_District'].fillna(0,inplace=True)

    # write the results out for the next step 
    print("Writing results out...")
    # os.makedirs(args.output_data, exist_ok=True)
    df.to_csv((Path(args.output_data) /"ReplacedMissingFeatures.csv"), index=False)

    print("Done!")

arguments = [
    ("input_data", str, "Name of the folder containing input data"),
    ("output_data",str, "Name of folder we will write results to")
]
args = utils.parse_args_list(arguments)
main(args)