from decouple import config
import macros_mapa

class PathFinderCell:
    def __init__(self, posX, posY):
        self.i = posX
        self.j = posY
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.previous = None
        self.isObstacle = False
        self.closed = False
        self.value = 1

    def setIsObstacle(self, isObstacle):
        self.isObstacle = isObstacle

    def getIsObstacle(self):
        return self.isObstacle

    def addNeighbors(self, grid, rows, cols):
        i = self.i
        j = self.j
        if i < cols-1 and grid[self.i + 1][j].isObstacle == False:
            self.neighbors.append(grid[self.i + 1][j])
        if i > 0 and grid[self.i - 1][j].isObstacle == False:
            self.neighbors.append(grid[self.i - 1][j])
        if j < rows-1 and grid[self.i][j + 1].isObstacle == False:
            self.neighbors.append(grid[self.i][j + 1])
        if j > 0 and grid[self.i][j - 1].isObstacle == False:
            self.neighbors.append(grid[self.i][j - 1])

    def reset(self):
        self.f = 0
        self.g = 0
        self.h = 0
        self.previous = None
        self.closed = False

class PathFinder:

    def __init__(self, mapDefinition):
        self.__mapDefinition = mapDefinition
        self.rows = self.__mapDefinition.getHorizontalSize()
        self.cols = self.__mapDefinition.getVerticalSize()
        self.grid = [0 for i in range(self.cols)]

        # create 2d array that represents the map
        for i in range(self.cols):
            self.grid[i] = [0 for i in range(self.rows)]

        # Initialize grid with cells
        for i in range(self.cols):
            for j in range(self.rows):
                self.grid[i][j] = PathFinderCell(i, j)

        # Initialize cells with map definition
        for i in range(self.cols):
            for j in range(self.rows):
                if( self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_BORDER or
                    self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_OBSTACLE  ):
                    self.grid[i][j].setIsObstacle(True)
                elif(self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_OCCUPABLE):
                    self.grid[i][j].setIsObstacle(False)
                else:
                    print("ERROR map cell definition unknown")

        # Initialize neighbors for each cell
        for i in range(self.cols):
            for j in range(self.rows):
                self.grid[i][j].addNeighbors(self.grid, self.rows, self.cols)

    def calculatePath(self, startX, startY, endX, endY):
        finished = False
        iterations = 0
        maxIterations = int(config('PATH_FINDER_MAX_ITERATIONS'))

        start = self.__getCell(startX, startY)
        end = self.__getCell(endX, endY)

        if(start == None or end == None or start.getIsObstacle() == True or end.getIsObstacle() == True):
            print("ERROR PATH FINDER - Invalid coordinates")
            return None

        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.grid[i][j].reset()

        openSet = []
        closedSet = []
        openSet.append(start)

        while(not finished):

            iterations = iterations + 1

            if(len(openSet) > 0):
                lowestIndex = 0
                for i in range(len(openSet)):
                    if openSet[i].f < openSet[lowestIndex].f:
                        lowestIndex = i

                current = openSet[lowestIndex]
                openSet.pop(lowestIndex)
                closedSet.append(current)
                current.closed = True

                # FINISHED CALCULATING or max iterations reached
                if(iterations >= maxIterations):
                    print("ERROR PATH FINDER - No path found for given coordinates (max iterations reached)")
                    finished = True
                    return []
                elif(current == end):
                    pathDistance = current.f
                    print(f"DONE - Distance: {pathDistance} // Iterations: {iterations}")

                    seqParams = []
                    seqParams = self.__getSequenceCoordinates(current)
                    #print(seqParams)
                    finished = True
                    return seqParams

                neighbors = current.neighbors
                for i in range(len(neighbors)):
                    neighbor = neighbors[i]
                    if(neighbor not in closedSet):
                        tempG = current.g + current.value
                        if(neighbor in openSet):
                            if(neighbor.g > tempG):
                                neighbor.g = tempG
                        else:
                            neighbor.g = tempG
                            openSet.append(neighbor)

                    neighbor.h = self.__heuristic(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h

                    if(neighbor.previous == None):
                        neighbor.previous = current

    def __getCell(self, x, y):
        if((x >= self.cols or x < 0) or (y >= self.rows or y < 0)):
            return None
        else:
            return self.grid[x][y]

    def __heuristic(self, n, e):
        d = abs(n.i - e.i) + abs(n.j - e.j)
        return d

    # returns a list of (X,Y) coordinates to move along the map
    def __getSequenceCoordinates(self, cellSequence):
        currentCell = cellSequence
        reversedCellSequence = []
        orderedCellSequence = []
        coordinatesPathSequence = []

        # get ordered sequence from cell sequence pointers
        for i in range(round(cellSequence.f)):
            reversedCellSequence.append(currentCell)
            if(currentCell.previous != None):
                currentCell = currentCell.previous
        reversedCellSequence.append(currentCell)

        #print("#### SECUENCIA ------------------")
        for i in reversed(reversedCellSequence):
            orderedCellSequence.append(i)
            coordinatesPathSequence.append((i.i, i.j))
            #print(f"X:{i.i} Y:{i.j}")
        return coordinatesPathSequence

    # returns a list of speeds and distances for the robot to drive along the path
    def __getSequenceParameters(self, cellSequence):
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

        #print("#### SECUENCIA ------------------")
        for i in reversed(reversedCellSequence):
            orderedCellSequence.append(i)
            #print(f"X:{i.i} Y:{i.j}")

        #print(f"START ({orderedCellSequence[0].i},{orderedCellSequence[0].j})")
        #print(f"END ({orderedCellSequence[len(orderedCellSequence)-1].i},{orderedCellSequence[len(orderedCellSequence)-1].j})")
        print()

        direction = 0 # 0 = upwards / 1 = right / 2 = downwards / 3 = left
        directionAux = 0 # robot is supposed to start "looking upwards"
        for i in range(len(orderedCellSequence)-1):
            deltaX = orderedCellSequence[i+1].i - orderedCellSequence[i].i
            deltaY = orderedCellSequence[i+1].j - orderedCellSequence[i].j
            #print(f"delta ({deltaX},{deltaY})")

            if(deltaX!=0 and deltaY!=0):
                print("Error - Unable to move along 2 axis at the same time")
                # FIXME hacer de ultima que capture el error y lo divida en 2 movimientos separados, ver

            #if(i != 0 and direction != directionAux): # ignore first iteration because i do not know the direction of the first movement 
                # must perform a turn
                #directionAux = direction

            if(deltaX>0 and deltaX==1 and deltaY==0):
                # move right
                print("DERECHA")
                #if(mustAppendTurn):
                #    pathSequence.append(asdasd)

                pathSequence.append([0.25, 0.25, 0, oneCellDistance])
                direction = 1
            elif(deltaX<0 and deltaX==-1 and deltaY==0):
                # move left
                print("IZQUIERDA")
                pathSequence.append([-0.25, -0.25, 0, oneCellDistance])
                direction = 3
            elif(deltaY>0 and deltaY==1 and deltaX==0):
                # move downwards
                print("ABAJO")
                pathSequence.append([-0.25, 0.25, 0, oneCellDistance])
                direction = 2
            elif(deltaY<0 and deltaY==-1 and deltaX==0):
                # move upwards
                print("ARRIBA")
                pathSequence.append([0.25, -0.25, 0, oneCellDistance])
                direction = 0

            # FIXME agregar filtro para agregar movimientos de rotacion al tener que cambiar de direccion

        # messages generated with format [vel_x; vel_y; theta; setpoint]
        return pathSequence

