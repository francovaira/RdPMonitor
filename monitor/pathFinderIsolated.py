import sys
import math
import time

class spot:
    def __init__(self, x, y):
        self.i = x
        self.j = y
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.previous = None
        self.obs = False
        self.closed = False
        self.value = 1

    # def show(self, color, st):
    #     if self.closed == False :
    #         pygame.draw.rect(screen, color, (self.i * w, self.j * h, w, h), st)
    #         pygame.display.update()

    # def path(self, color, st):
    #     pygame.draw.rect(screen, color, (self.i * w, self.j * h, w, h), st)
    #     pygame.display.update()

    def addNeighbors(self, grid):
        i = self.i
        j = self.j
        if i < cols-1 and grid[self.i + 1][j].obs == False:
            self.neighbors.append(grid[self.i + 1][j])
        if i > 0 and grid[self.i - 1][j].obs == False:
            self.neighbors.append(grid[self.i - 1][j])
        if j < rows-1 and grid[self.i][j + 1].obs == False:
            self.neighbors.append(grid[self.i][j + 1])
        if j > 0 and grid[self.i][j - 1].obs == False:
            self.neighbors.append(grid[self.i][j - 1])

cols = 10
rows = 15
grid = [0 for i in range(cols)]
openSet = []
closedSet = []

# create 2d array
for i in range(cols):
    grid[i] = [0 for i in range(rows)]

# Create Spots
for i in range(cols):
    for j in range(rows):
        grid[i][j] = spot(i, j)

# Set start and end node
start = grid[1][1]
end = grid[8][8]

for i in range(0,rows):
    grid[0][i].obs = True
    grid[cols-1][i].obs = True
for i in range(0,cols):
    grid[i][rows-1].obs = True
    grid[i][0].obs = True

openSet.append(start)

for i in range(cols):
    for j in range(rows):
        grid[i][j].addNeighbors(grid)

def heurisitic(n, e):
    d = abs(n.i - e.i) + abs(n.j - e.j)
    return d

# returns a list of speeds and distances for the robot to drive along the path
def getSequenceParameters(cellSequence):
    currentCell = cellSequence
    reversedCellSequence = []
    orderedCellSequence = []
    pathSequence = []
    oneCellDistance = 1

    # get ordered sequence from cell sequence pointers
    for i in range(round(cellSequence.f)):
        reversedCellSequence.append(currentCell)
        if(currentCell.previous != None):
            currentCell = currentCell.previous
    reversedCellSequence.append(currentCell)

    print("#### SECUENCIA ------------------")
    for i in reversed(reversedCellSequence):
        orderedCellSequence.append(i)
        print(f"X:{i.i} Y:{i.j}")

    print(f"START ({orderedCellSequence[0].i},{orderedCellSequence[0].j})")
    print(f"END ({orderedCellSequence[len(orderedCellSequence)-1].i},{orderedCellSequence[len(orderedCellSequence)-1].j})")
    print()

    for i in range(len(orderedCellSequence)-1):
        deltaX = orderedCellSequence[i+1].i - orderedCellSequence[i].i
        deltaY = orderedCellSequence[i+1].j - orderedCellSequence[i].j
        #print(f"delta ({deltaX},{deltaY})")

        if(deltaX!=0 and deltaY!=0):
            print("Error - Unable to move along 2 axis at the same time")
            # FIXME hacer de ultima que capture el error y lo divida en 2 movimientos separados, ver

        if(deltaX>0 and deltaX==1 and deltaY==0):
            # move right
            print("DERECHA")
            pathSequence.append([0.25, 0.25, 0, oneCellDistance])
        elif(deltaX<0 and deltaX==-1 and deltaY==0):
            # move left
            print("IZQUIERDA")
            pathSequence.append([-0.25, -0.25, 0, oneCellDistance])
        elif(deltaY>0 and deltaY==1 and deltaX==0):
            # move downwards
            print("ABAJO")
            pathSequence.append([-0.25, 0.25, 0, oneCellDistance])
        elif(deltaY<0 and deltaY==-1 and deltaX==0):
            # move upwards
            print("ARRIBA")
            pathSequence.append([0.25, -0.25, 0, oneCellDistance])

    # messages generated with format [vel_x; vel_y; theta; setpoint]
    return pathSequence

def main():

    finished = False
    iterations = 0

    while(not finished):

        iterations = iterations + 1

        if len(openSet) > 0:
            lowestIndex = 0
            for i in range(len(openSet)):
                if openSet[i].f < openSet[lowestIndex].f:
                    lowestIndex = i

            current = openSet[lowestIndex]
            openSet.pop(lowestIndex)
            closedSet.append(current)
            current.closed = True

            # FINISHED CALCULATING
            if current == end:
                print('done', current.f)
                pathDistance = current.f

                seqParams = []
                seqParams = getSequenceParameters(current)
                print(seqParams)
                print(f"Iterations {iterations}")
                finished = True
                break

            neighbors = current.neighbors
            for i in range(len(neighbors)):
                neighbor = neighbors[i]
                if neighbor not in closedSet:
                    tempG = current.g + current.value
                    if neighbor in openSet:
                        if neighbor.g > tempG:
                            neighbor.g = tempG
                    else:
                        neighbor.g = tempG
                        openSet.append(neighbor)

                neighbor.h = heurisitic(neighbor, end)
                neighbor.f = neighbor.g + neighbor.h

                if neighbor.previous == None:
                    neighbor.previous = current

    exit()

while True:
    main()
