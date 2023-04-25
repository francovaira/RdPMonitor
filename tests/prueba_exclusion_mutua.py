import pandas as pd
import os
  
def transitions(robot_id):
    # reading given csv file  and creating dataframe
    websites = pd.read_csv("./LOG_OUTPUT.txt", header = None)
    
    # # adding column headings
    websites.columns = ['Timestamp', 'Robot_ID', 'Message_ID']

    websites.sort_values('Timestamp', ascending=True)

    websites = websites.drop(['Timestamp'], axis=1)

    # # store dataframe into csv file
    websites.to_csv('./timestamps.csv', index = None)

    with open('timestamps.csv', 'r') as f_in:


        data = f_in.read().replace('\n', ',')
        transition_fired = data.count(f"{robot_id},1,{robot_id},2,{robot_id},3,{robot_id},4,{robot_id},5")
        count_fired_after_policy = data.count(f"10,{robot_id},2,{robot_id},3,{robot_id},4,{robot_id},5")
        count_encoladas = data.count(f"{robot_id},20")

        # print('A', 'Fired: ', transition_fired_a, 'Blocked: ', count_encoladas_a, "Fired after blocker: ", count_fired_after_policy_a, 'Total Fired: ', (transition_fired_a+count_fired_after_policy_a))
        # print('B', 'Fired: ', transition_fired_b, 'Blocked: ', count_encoladas_b, "Fired after blocker: ", count_fired_after_policy_b, 'Total Fired: ', (transition_fired_b+count_fired_after_policy_b))
        # print('C', 'Fired: ', transition_fired_c, 'Blocked: ', count_encoladas_c, "Fired after blocker: ", count_fired_after_policy_c, 'Total Fired: ', (transition_fired_c+count_fired_after_policy_c))

    #Delete tmp file
    os.remove('timestamps.csv')

    return transition_fired, count_fired_after_policy, count_encoladas 

transition_fired, count_fired_after_policy, count_encoladas = transitions('ROB_C')
print(f"{transition_fired+count_fired_after_policy}, {count_fired_after_policy}, {count_encoladas}")