import pandas as pd
import os 
import argparse
import yaml

def build_df_from_folder(folder_path):  
    # path = {
    #     'folder': folder_path
    # }
    # tbl = mltable.from_delimited_files(paths=[path]) # heavier, and specified for AML ecosystem
    # df = tbl.to_pandas_dataframe()
    
    print(os.listdir(folder_path)) # for small file 
    file_list = [] 
    for filename in os.listdir(folder_path):
        i_input = pd.read_csv(os.path.join(folder_path, filename))
        file_list.append(i_input)

    df = pd.concat(file_list)

    return df  


def parse_args_list(arr):
    parser = argparse.ArgumentParser() 
    for arg_name, arg_type, arg_desc in arr:
        parser.add_argument(f"--{arg_name}", type=arg_type, help=arg_desc)

    args = parser.parse_args()

    # for arg_name, arg_type, arg_desc in arr:
    #     if "" != arg_desc:
    #         print(f"{arg_desc}: {getattr(args, arg_name)}")

    print(" ".join(f"{k}={v}" for k, v in vars(args).items()))

    return args

def get_package_version(conda_path, pkg_name="scikit-learn"):
    with open(conda_path) as file:
        conda = yaml.safe_load(file)

    pip_block = next(
        p["pip"] for p in conda["dependencies"] if isinstance(p, dict) and "pip" in p
    )

    return next(
         (p.split("==")[1] for p in pip_block
         if p.startswith(f"{pkg_name}==")),
         None
    ) 

if __name__ == "__main__":
    arr = [
        ("input_data",str, "Name of the folder containing input data"),
        ("output_data",str, "Name of folder we will write results to")
    ]

    rs = parse_args_list(arr)