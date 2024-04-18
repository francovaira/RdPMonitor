import logging

# esta clase seria la encargada de distribuir los jobs - en teoria cualquier robot podria hacer cualquier job
class JobManager:
    def __init__(self):
        self.__robotsJobsQueue = {} # se almacenan las colas donde se van a poner trabajos en los hilos linkeadas con el nombre del robot en un diccionario

    def addRobotJobQueue(self, robotID, jobQueue):
        self.__robotsJobsQueue.update({robotID:jobQueue})
        logging.debug(f'[{__name__}] added job queue robot {robotID}')

    def sendJobToRobot(self, robotID, job):
        if(not type(job) == Job):
            logging.error(f'unable to send JOB to robot {robotID}')
        try:
            self.__robotsJobsQueue[robotID].put(job)
        except Exception as e:
            logging.error(f'unable to put a job to robot {robotID}')

class Path:
    def __init__(self, initPos, endPos):
        self.__initPos = initPos
        self.__endPos = endPos

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

    def getTransitionsPathSequence(self):
        return self.__transitionsPathSequence

    def getCoordinatesPathSequence(self):
        return self.__coordinatesPathSequence

    def getTransitionIndex(self):
        return self.__transitionIndex

    def getNextTransitionToExecute(self):
        transitionsSequence = self.getTransitionsPathSequence()
        transitionIndex = self.getTransitionIndex()
        if(not len(transitionsSequence)):
            logging.error(f'[{__name__}] Transition sequence empty - must initialize paths')
            return -1
        return transitionsSequence[transitionIndex]

    # devuelve true si termino el camino, si no termino de recorrer retorna false
    def updateNextTransitionToExecute(self):
        self.setTransitionIndex(self.getTransitionIndex() + 1)
        if(self.getTransitionIndex() >= len(self.getTransitionsPathSequence())): # path finished
            return True
        return False
        # if(self.getTransitionIndex() < len(self.getTransitionsPathSequence())): # path not finished yet
        #     self.setTransitionIndex(self.getTransitionIndex() + 1)
        #     return False
        # return True

    def setTransitionIndex(self, transitionIndex):
        self.__transitionIndex = transitionIndex

    def setCoordinatesPathSequence(self, pathCoordinatesSequence): # FIXME por ahora esta sin usarse, ver si hace falta
        self.__coordinatesPathSequence = pathCoordinatesSequence

    def setTransitionsPathSequence(self, pathTransitionSequence):
        self.__transitionsPathSequence = pathTransitionSequence
