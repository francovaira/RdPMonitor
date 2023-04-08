from JobManager import Job

class RobotThreadExecutor:
    def __init__(self, robotID, monitor):
        self.__monitor = monitor
        self.__robotID = robotID
        self.__jobs = []

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

        transitionToExecute = transitionsSequence[transitionIndex]
        if(self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)): # si pudo disparar, busco la siguiente transicion
            nextTransitionIndex = transitionIndex + 1
            currentJob.setTransitionIndex(nextTransitionIndex)

            if(nextTransitionIndex>= len(transitionsSequence)):
                print(f"SEQUENCE FINISHED AT THE END @{self.__robotID}")
                return False
        return True
