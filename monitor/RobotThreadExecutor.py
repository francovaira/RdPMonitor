
class Path:
    def __init__(self, initPosX, initPosY, endPosX, endPosY):
        self.__initPos = tuple((initPosX, initPosY))
        self.__endPos = tuple((endPosX, endPosY))

    def getInitPos(self):
        return self.__initPos

    def getEndPos(self):
        return self.__endPos

# esto tiene basicamente un conjunto de paths (compuestos cada uno por un punto o mas) para realizar
class Job:
    def __init__(self):
        self.__paths = []
        self.__transitionsPathSequence = []
        self.__coordinatesPathSequence = []
        self.__transitionIndex = 0

    def addPath(self, path):
        if(type(path) == Path):
            self.__paths.append(path)

    def addPathByCoordinates(self, initPosX, initPosY, endPosX, endPosY):
        if(type(initPosX) == int and type(initPosY) == int and type(endPosX) == int and type(endPosY) == int):
            self.__paths.append(Path(initPosX, initPosY, endPosX, endPosY))

    def getPaths(self):
        return self.__paths

    def getTransitionsSequence(self):
        return self.__transitionsPathSequence

    def getTransitionIndex(self):
        return self.__transitionIndex

    def setTransitionIndex(self, transitionIndex):
        self.__transitionIndex = transitionIndex

    def setCoordinatesPathSequence(self, pathCoordinatesSequence): # FIXME por ahora esta sin usarse, ver si hace falta
        self.__coordinatesPathSequence = pathCoordinatesSequence

    def setTransitionsPathSequence(self, pathTransitionSequence):
        self.__transitionsPathSequence = pathTransitionSequence


class RobotThreadExecutor:
    def __init__(self, robotID, monitor):
        self.__monitor = monitor
        self.__robotID = robotID
        self.__jobs = []
    #     self.__paths = []
    #     self.__transitionSequence = [] # por ahora esto esta aca, deberia separarse y que sea parte del job en si
    #     self.__coordinatesPathSequence = [] # por ahora esto esta aca, deberia separarse y que sea parte del job en si
    #     self.__transitionIndex = 0

    # def addPath(self, path):
    #     if(type(path) == Path):
    #         self.__paths.append(path)
    #         print(f"New path added for robot {self.__robotID}")

    # def addPathByCoordinates(self, initPosX, initPosY, endPosX, endPosY):
    #     if(type(initPosX) == int and type(initPosY) == int and type(endPosX) == int and type(endPosY) == int):
    #         self.__paths.append(Path(initPosX, initPosY, endPosX, endPosY))
    #         print(f"New path added by coordinates for robot {self.__robotID}")

    def addJob(self, job):
        if(type(job) == Job):
            self.__jobs.append(job)

    # calculates coordinates sequence then transition sequence for each job and places robot in init position. Sets everything to start running on the thread
    def startPaths(self):
        if(not len(self.__jobs) or len(self.__jobs) > 1): # FIXME por ahora no soporta mas de 1 job
            print(f"NO JOBS DEFINED -- WILL DO NOTHING, EXITING...")
            exit()

        # por aca deberia checkear que los path (si hay mas de uno) sean continuos - es decir, no seria valido ir de (1,1 a 5,5) y despues de (3,2 a 4,1)
        # capaz se podria hacer que calcule la trayectoria del tramo faltante de ultima

        # self.__coordinatesPathSequence = self.__getCoorinatesSequence(self.__paths)
        # self.__transitionSequence = self.__monitor.getTransitionSequence(self.__coordinatesPathSequence)
        # self.__monitor.setRobotInCoordinate(self.__coordinatesPathSequence[0], self.__robotID)

        for job in self.__jobs:
            coordinatesSequence = self.__getCoorinatesSequence(job.getPaths())
            transitionsSequence = self.__monitor.getTransitionSequence(coordinatesSequence)
            job.setCoordinatesPathSequence(coordinatesSequence)
            job.setTransitionsPathSequence(transitionsSequence)
            self.__monitor.setRobotInCoordinate(coordinatesSequence[0], self.__robotID)
        print(f"STARTED PATHS || COORDINATES SEQUENCE = {coordinatesSequence} // TRANSITIONS SEQUENCE = {transitionsSequence}")

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

        currentJob = self.__jobs[0]

        transitionsSequence = currentJob.getTransitionsSequence()
        transitionIndex = currentJob.getTransitionIndex()

        if(not len(transitionsSequence)):
            print("ERROR - Transition sequence empty - must initialize paths")
            exit()

        if(transitionIndex >= len(transitionsSequence)):
            print(f"SEQUENCE FINISHED -- HERE AT THE BEGINNING @{self.__robotID}")
            return False

        #transitionIndex = transitionIndex % len(transitionsSequence) # capaz esto esta de mas por ser que se checkea en el if de arriba si llego al final, no se pasaria de cuenta nunca
        #currentJob.setTransitionIndex(transitionIndex)
        transitionToExecute = transitionsSequence[transitionIndex]
        if(self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)): # si pudo disparar, busco la siguiente transicion
            nextTransitionIndex = transitionIndex + 1
            currentJob.setTransitionIndex(nextTransitionIndex)

            if(nextTransitionIndex>= len(transitionsSequence)):
                print(f"SEQUENCE FINISHED AT THE END @{self.__robotID}")
                return False
        return True

        # transitionsSequence = self.__jobs[0].getTransitionsSequence()

        # if(not len(transitionsSequence)):
        #     print("ERROR - Transition sequence empty - must initialize paths")
        #     exit()

        # if(self.__transitionIndex >= len(transitionsSequence)):
        #     print(f"SEQUENCE FINISHED -- HERE AT THE BEGINNING @{self.__robotID}")
        #     return False

        # self.__transitionIndex = self.__transitionIndex % len(transitionsSequence)
        # transitionToExecute = transitionsSequence[self.__transitionIndex]
        # if(self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)): # si pudo disparar, busco la siguiente transicion
        #     self.__transitionIndex = self.__transitionIndex + 1

        #     if(self.__transitionIndex >= len(transitionsSequence)):
        #         print(f"SEQUENCE FINISHED AT THE END @{self.__robotID}")
        #         return False
        # return True