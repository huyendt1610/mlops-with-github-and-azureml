from pathlib import Path
import pandas as pd 
import utils
import numpy as np  

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

arguments = [
    ("input_data", str, "Name of the folder containing input data"),
    ("output_data",str, "Name of folder we will write results to")
]

args = utils.parse_args_list(arguments)
df = utils.build_df_from_folder(args.input_data)

# Feature selection 
df.drop(['Tract', 'Hardship_Index', 'Issued_date', 'License_Plate_State', 'Plate_Type'], axis=1, inplace=True)

# write the results to the next step 
print("Writing results out...")
df.to_csv((Path(args.output_data) / "FeatureSelection.csv"),index=False)

print("Done")