# importing pandas library
import pandas as pd
  
# reading given csv file 
# and creating dataframe
websites = pd.read_csv("../monitor/LOG_OUTPUT.txt"
                       ,header = None)
  
# adding column headings
websites.columns = ['Timestamp', 'Robot_ID', 'Transition', 'FireCount']
  
# store dataframe into csv file
websites.to_csv('./timestamps.csv', 
                index = None)