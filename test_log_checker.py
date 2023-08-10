import os
import pandas as pandasForSortingCSV

# assign dataset
csvData = pandasForSortingCSV.read_csv("/home/franco/Documents/RdPMonitor/RdPMonitor/LOG_OUTPUT.txt")


def fileWrite(list2write, filename):
    try:
        absolutePath = os.path.dirname(os.path.realpath(__file__)) # get the absolute path of the directory the script is in
        #writeFilePath = os.path.join(absolutePath, "petri_nets", f"{filename}") # construct the path to the file in the subdirectory # FIXME hacer un define/config
        writeFilePath = os.path.join(absolutePath, f"{filename}") # construct the path to the file in the subdirectory # FIXME hacer un define/config
        writeFile=open(writeFilePath,"w")
        writeFile.write(str(list2write))
        writeFile.close()
    except Exception as e:
            print(str(e))
            print(f"EXCEPTION - Unable to write LOG CHECKER file <{filename}>")

# displaying unsorted data frame
print("\nBefore sorting:")
#print(csvData)

# sort data frame
csvData.sort_values(by=csvData.columns[0], # esto hace que ordene por la columna 0, es decir el timestamp
                    axis=0,
                    ascending=[True],
                    inplace=True)

# displaying sorted data frame
print("\nAfter sorting:")
#print(csvData)
#fileWrite(csvData.to_string(), "LOG_OUTPUT_SORTED")
csvData.to_csv('monitor/LOG_OUTPUT_SORTED.csv', index=False, float_format='%.5f')
print("\nbye...")

# ################# hasta aca obtiene el ordenado dentro de csvData

file1 = open('monitor/LOG_OUTPUT_SORTED.csv', 'r')
Lines = file1.readlines()
priorTimestamp = 0
priorRobot = ""

# possible states
# [1,2,3,4,5]
# [1,2,3,4,5,10]
# [1,20,2,3,4,5]

states = []

states.append([1,2,3,4,5])
states.append([1,2,3,4,5,10])
states.append([1,20,2,3,4,5])

class Robot:
    def __init__(self, rob_id):
        self.nextExpectedStates = []
        self.currentState = []
        self.rob_id = rob_id

robotsList = []
def addRobot(robotID):
    if(any(elem.rob_id == robotID.rob_id for elem in robotsList)): # check for duplicates
        #print(f"ERROR - The robot <{robotID}> is trying to add another copy of itself")
        pass
    else:
        robotsList.append(robotID)
        print(f"APPENDED {robotID.rob_id}")

def getRobot(robotID):
    for robot in robotsList:
        if(robot.rob_id == robotID):
            return robot

for line in Lines:

    splitted = line.split(",")

    timestamp = float(splitted[0])
    robot = splitted[1]
    action = int(splitted[2])

    print(f"timestamp {timestamp}")

    if(priorTimestamp == timestamp):
        if(priorRobot != robot):
            print("ERRORRRRRR - TIMESTAMPS EN CUALQUIERA")
            exit()

    if(priorTimestamp > timestamp):
        print("ERRORRRRRR - TIMESTAMPS EN CUALQUIERA")
        exit()

    priorRobot = robot
    priorTimestamp = timestamp

    addRobot(Robot(robot))
    robot_object = getRobot(robot)

    robot_object.currentState.append(action)
    robot_possible_states = []

    for possible_state in states:

        print(f"checkeando el posible estado {possible_state}")

        if(len(possible_state) >= len(robot_object.currentState)):
            robot_possible_states.append(possible_state)
            for i in range(len(robot_object.currentState)):
                print(f"CHECKEANDO CURRENT STATE {robot_object.currentState[i]} CONTRA POSSIBLE {possible_state[i]}")
                if(robot_object.currentState[i] != possible_state[i]): # is a mismatch, remove from list
                    print(f"remuevo el estado, no coincide")
                    robot_possible_states.pop() # removes the element?
                    break
        else:
            print(f"SE RE PASO DE TAMAÑO EL CURRENT STATE PARA EL POSSIBLE {possible_state}")

    if(len(robot_possible_states) == 0):
        print("ERRORRRRRR EL ROBOT NO MATCHEAAAA")
        exit()
    else:
        print(f"QUEDO MAS DE UN POSIBLE COSO // {robot_possible_states}")
        if(len(robot_possible_states) == 1):
            if(len(robot_possible_states[0]) == len(robot_object.currentState)):
                print(f"SE LLENOOOOOO - IMPRIME < curr_state {robot_object.currentState} > // < poss_states {robot_possible_states} >")
                robot_object.currentState = []


#for robot in robotsList:
#    print(robot.rob_id)

