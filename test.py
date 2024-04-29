import pandas as pd

# save filepath to variable for easier access
melbourne_file_path = 'C:/Users/Allen/Downloads/AAPL.csv'
print("path")
# read the data and store data in DataFrame titled melbourne_data
melbourne_data = pd.read_csv(melbourne_file_path) 
print("data")
# print a summary of the data in Melbourne data
print(melbourne_data.describe())