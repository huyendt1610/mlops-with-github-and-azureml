import argparse
import utils
from pathlib import Path
from sklearn.model_selection import train_test_split

# parser = argparse.ArgumentParser() 
# parser.add_argument("--input_data",type=str, help="The folder Name for input data")
# parser.add_argument('--output_data_train',type=str, help='Name of the folder to write training data to')
# parser.add_argument('--output_data_test',type=str, help='Name of the folder to write test data to')
# args = parser.parse_args() 

# lines = [
#     f'Input data path: {args.input_data}',
#     f'Output training data path: {args.output_data_train}',
#     f'Output test data path: {args.output_data_train}',
# ]

# for line in lines: 
#     print(line)


arguments = [
    ("input_data", str, "The folder Name for input data"),
    ("output_data_train",str, "Name of the folder to write training data to"),
    ("output_data_test", str, 'Name of the folder to write test data to')
]

args = utils.parse_args_list(arguments)
df = utils.build_df_from_folder(args.input_data)

df = df.head(100000)

train_df, test_df = train_test_split(df, test_size=0.2, random_state=666)

print("Writing results out...")
train_df.to_csv((Path(args.output_data_train)/"TrainData.csv"), index=False)
test_df.to_csv((Path(args.output_data_test)/"TestData.csv"), index=False)

print("Done!")