# importing pandas library
# import pandas as pd
  
# # reading given csv file 
# # and creating dataframe
# websites = pd.read_csv("../monitor/LOG_OUTPUT.txt"
#                        ,header = None)
  
# # adding column headings
# websites.columns = ['Timestamp', 'Robot_ID', 'Transition', 'FireCount']
  
# # store dataframe into csv file
# websites.to_csv('./timestamps.csv', 
#                 index = None)

#open text file in read mode
text_file = open('../monitor/LOG_OUTPUT.txt', 'r')
 
#read whole file to a string
data = text_file.read()
 
#close file
text_file.close()
 
transition_fired_a = data.count('ROB_A,1,ROB_A,2,ROB_A,3,ROB_A,4,ROB_A,5')
transition_fired_b = data.count('ROB_B,1,ROB_B,2,ROB_B,3,ROB_B,4,ROB_B,5')
transition_fired_c = data.count('ROB_C,1,ROB_C,2,ROB_C,3,ROB_C,4,ROB_C,5')

count_fired_after_policy_a =data.count('10,ROB_A,2,ROB_A,3,ROB_A,4,ROB_A,5')
count_fired_after_policy_b =data.count('10,ROB_B,2,ROB_B,3,ROB_B,4,ROB_B,5')
count_fired_after_policy_c =data.count('10,ROB_C,2,ROB_C,3,ROB_C,4,ROB_C,5')

count_encoladas_a = data.count('ROB_A,20')
count_encoladas_b = data.count('ROB_B,20')
count_encoladas_c = data.count('ROB_C,20')

print('A', 'Fired: ', transition_fired_a, 'Blocked: ', count_encoladas_a, "Fired after blocker: ", count_fired_after_policy_a, 'Total Fired: ', (transition_fired_a+count_fired_after_policy_a))
print('B', 'Fired: ', transition_fired_b, 'Blocked: ', count_encoladas_b, "Fired after blocker: ", count_fired_after_policy_b, 'Total Fired: ', (transition_fired_b+count_fired_after_policy_b))
print('C', 'Fired: ', transition_fired_c, 'Blocked: ', count_encoladas_c, "Fired after blocker: ", count_fired_after_policy_c, 'Total Fired: ', (transition_fired_c+count_fired_after_policy_c))
