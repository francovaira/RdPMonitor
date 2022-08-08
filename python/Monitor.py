import threading
import time

class Monitor:

    def __init__(self, lock, petriNet):
        self.monitorLock = lock
        self.petriNet = petriNet
        self.conditions = []
        self.fireCount = 0

        # initialize conditions for transitions and their threads
        for i in range(0, self.petriNet.transitionCount):
            cond = threading.Condition(self.monitorLock) # reference to the main lock
            self.conditions.append(cond)

    def fireCountIncrement(self):
        self.fireCount = self.fireCount+1

    def monitor_disparar(self, transition, id):
        with self.conditions[transition]:
            k = self.petriNet.solicitud_disparo(transition)
            while(k == 0):
                print(f"{time.time()} [{id}] ### No sensibilizada {transition} -- esperando...")
                self.conditions[transition].wait() # espera que otro hilo lo despierte
                k = self.petriNet.solicitud_disparo(transition)

            # disparar efectivamente - obtener el nuevo marcado
            self.fireCountIncrement()
            print(f"{time.time()} [{id}] ### Si sensibilizada, disparo: {transition} __ CANT DISPAROS {self.fireCount}")
            self.petriNet.red_disparar(transition)
            self.petriNet.print_marcado()
            self.conditions[transition].notify_all()

        # notify for other conditions and potential waiting threads
        for i in range(0, self.petriNet.transitionCount):
            with self.conditions[i]:
                self.conditions[i].notify_all()


