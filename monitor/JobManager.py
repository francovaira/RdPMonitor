
# esta clase seria la encargada de distribuir los jobs - en teoria cualquier robot podria hacer cualquier job
class JobManager:
    def __init__(self):
        self.__robotsJobsQueue = {} # se almacenan las colas donde se van a poner trabajos en los hilos linkeadas con el nombre del robot en un diccionario

    def addRobotJobQueue(self, robotID, jobQueue):
        self.__robotsJobsQueue.update({robotID:jobQueue})
        #print(f"ADDED JOB QUEUE OF ROBOT {robotID} || {self.__robotsJobsQueue}")

    def sendJobToRobot(self, robotID, job):
        if(not type(job) == Job):
            print("ERROR - unable to send JOB to robot")

        try:
            self.__robotsJobsQueue[robotID].put(job)
            print(f"ADDED TO ROBOT {robotID} THE JOB {job.getPaths()}")
        except Exception as e:
            print(str(e))
            print(f"EXCEPTION - Unable to put a job to robot {robotID}")


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
