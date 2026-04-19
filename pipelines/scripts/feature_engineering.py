import argparse
import os 
from pathlib import Path
import pandas as pd 
import pickle
import mlflow 
import mlflow.sklearn 
import sys  
import timeit 
import numpy as np  
import utils

def main(args): 
    print("Performing feature engineering...")

    # parser = argparse.ArgumentParser() 
    # parser.add_argument("--input_data",type=str,help="Name of the folder containing input data")
    # parser.add_argument("--output_data",type=str, help="Name of the folder we will write results out to")
    # args = parser.parse_args() 

    # lines =[
    #     f"Input data path: {args.input_data}",
    #     f"Output data path: {args.output_data}"
    # ]

    # for line in lines: 
    #     print(line)

    # print(os.listdir(args.input_data))

    # filelist=[]
    # for filename in os.listdir(args.input_data): 
    #     print(f"Reading file {filename}")
    #     with open(os.path.join(args.input_data, filename), "r") as f: 
    #         input_df = pd.read_csv(Path(args.input_data) /filename)
    #         filelist.append(input_df)

    # df = pd.concat(filelist)

    df = utils.build_df_from_folder(args.input_data)
    # print(len(df))
    # return 
    # Feature engineering steps 
    df["Issued_date"]=pd.to_datetime(df["Issued_date"])
    df["Issued_year"]=df['Issued_date'].dt.year 

    # categorize time based on hour of the day 
    # Note: cuts are right-aligned, so here I'm starting with -1 to get the 0-6 hour range 
    hour_bins =[-1,6,10,16,19,np.inf]
    hour_names=['Overnight','Morning','Midday','Afterwork','Evening']
    df['Time_of_day']=pd.cut(df['Issued_date'].dt.hour, bins=hour_bins,labels=hour_names)

    # license plate origin 
    conds=[
        df['License_Plate_State'].isin(['IL']), # 'In-state'
        df['License_Plate_State'].isin(['ON', 'ZZ', 'NB', 'AB', 'QU', 'MX', 'BC', 'MB', 'PE', 'NS', 'PQ', 'NF'])
    ]

    choices=['In-state','Out-of-country']
    df['License_plate_origin']=np.select(conds,choices,default='Out-of-state')

    # vehicle-type 

    conds=[
        df['Plate_Type']=='PAS',
        df['Plate_Type']=='TRK',
        df['Plate_Type']=='TMP',
    ]
    choices=['PAS','TRK','TMP']
    df['Vehicle_type']=np.select(conds,choices,default='Other')

    # Write the results out for the next step 
    print("Writing results out...")
    # os.makedirs(args.output_data, exist_ok=True)
    df.to_csv((Path(args.output_data)/"FeatureEngineering.csv"),index=False)

    print("Done!")

arguments = [
    ("input_data", str, "Name of the folder containing input data"),
    ("output_data",str, "Name of folder we will write results to")
]
args = utils.parse_args_list(arguments)
main(args)
