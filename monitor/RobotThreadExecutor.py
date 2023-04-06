

class Path:
    def __init__(self, initPosX, initPosY, endPosX, endPosY):
        self.__initPos = tuple((initPosX, initPosY))
        self.__endPos = tuple((endPosX, endPosY))

    def getInitPos(self):
        return self.__initPos

    def getEndPos(self):
        return self.__endPos

class RobotThreadExecutor:
    def __init__(self, robotID, monitor):
        self.__monitor = monitor
        self.__robotID = robotID
        self.__paths = []
        self.__transitionSequence = [] # por ahora esto esta aca, deberia separarse y que sea parte del job en si
        self.__coordinatesPathSequence = [] # por ahora esto esta aca, deberia separarse y que sea parte del job en si
        self.__transitionIndex = 0

    def addPath(self, path):
        if(type(path) == Path):
            self.__paths.append(path)
            print(f"New path added for robot {self.__robotID}")

    def addPathByCoordinates(self, initPosX, initPosY, endPosX, endPosY):
        if(type(initPosX) == int and type(initPosY) == int and type(endPosX) == int and type(endPosY) == int):
            self.__paths.append(Path(initPosX, initPosY, endPosX, endPosY))
            print(f"New path added by coordinates for robot {self.__robotID}")

    # calculates coordinates sequence then transition sequence, places robot in init position. Sets everything to start running on the thread
    def startPaths(self):
        if(not len(self.__paths)):
            print(f"NO PATHS DEFINED -- WILL DO NOTHING, EXITING...")
            exit()

        # por aca deberia checkear que los path (si hay mas de uno) sean continuos - es decir, no seria valido ir de (1,1 a 5,5) y despues de (3,2 a 4,1)
        # capaz se podria hacer que calcule la trayectoria del tramo faltante de ultima

        self.__coordinatesPathSequence = self.__getCoorinatesSequence(self.__paths)
        self.__transitionSequence = self.__monitor.getTransitionSequence(self.__coordinatesPathSequence)
        self.__monitor.setRobotInCoordinate(self.__coordinatesPathSequence[0], self.__robotID)
        print(f"STARTED PATHS || COORDINATES SEQUENCE = {self.__coordinatesPathSequence} // TRANSITIONS SEQUENCE = {self.__transitionSequence}")

    def __getCoorinatesSequence(self, paths):
        coordinatesSequence = []
        for path in paths:
            initPos = path.getInitPos()
            endPos = path.getEndPos()
            coordSeq = self.__monitor.calculatePath(initPos[0], initPos[1], endPos[0], endPos[1])

            if(len(coordinatesSequence) > 0):
                coordSeq.pop(0)
                coordinatesSequence.extend(coordSeq)
            else:
                coordinatesSequence = coordSeq
        return coordinatesSequence

    def run(self):

        if(not len(self.__transitionSequence)):
            print("ERROR - Transition sequence empty - must initialize paths")
            exit()

        if(self.__transitionIndex >= len(self.__transitionSequence)):
            print(f"SEQUENCE FINISHED -- HERE AT THE BEGINNING @{self.__robotID}")
            return False

        self.__transitionIndex = self.__transitionIndex % len(self.__transitionSequence)
        transitionToExecute = self.__transitionSequence[self.__transitionIndex]
        if(self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)): # si pudo disparar, busco la siguiente transicion
            self.__transitionIndex = self.__transitionIndex + 1

            if(self.__transitionIndex >= len(self.__transitionSequence)):
                print(f"SEQUENCE FINISHED AT THE END @{self.__robotID}")
                return False
        return True