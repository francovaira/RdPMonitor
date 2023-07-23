from integration_test import Setup
import multiprocessing
from multiprocessing import Process
from controllers.Controller import Controller
from views.Visualizer import Visualizer
from models.Model import Model

class App:
    def __init__(self):
        # self.title('Tkinter MVC Demo') 

        # create a model
        model = Model()

        # create a view and place it on the root window
        viz = Visualizer(1200, 800)
        # viz = Visualizer(1200, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

        # view = View(self)
        # view.grid(row=0, column=0, padx=10, pady=10)

        # create a controller
        controller = Controller(model, viz)

        # set the controller to view
        viz.setController(controller)
        # viz.createMap()
        # viz.run()
        # cualquier cosa que se ponga despues de esto no se va a ejecutar aunque los hilos terminen
        processVisualizer = multiprocessing.Process(target=viz.run())
        processVisualizer.start()


    # def main():

    #     map = Map()
    #     mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    #     mapVerticalSize = map.getMapDefinition().getVerticalSize()

    #     rdp = RdP(map)
    #     # mqttc, mqttc_robot_queue =  mqtt.main()
    #     monitor = Monitor(rdp, map.getPathFinder())
    #     viz = Visualizer(1200, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    #     # create threads for each robot
    #     threads = []
    #     thread_ROBOT_A = Thread(target=thread_run, args=(monitor, Robot('ROB_A')))
    #     thread_ROBOT_B = Thread(target=thread_run, args=(monitor, Robot('ROB_B')))
    #     # thread_ROBOT_B = Thread(target=thread_run, args=(monitor, 'ROB_B', map.getPathFinder(), mqttc, mqttc_queue))
    #     threads.append(thread_ROBOT_A)
    #     threads.append(thread_ROBOT_B)
    #     # threads.append(thread_ROBOT_C)
    #     thread_ROBOT_A.start()
    #     thread_ROBOT_B.start()
    #     # thread_ROBOT_C.start()

    #     processVisualizer = multiprocessing.Process(target=viz.run())
    #     processVisualizer.start()

    #     # wait for the threads to complete
    #     for thread in threads:
    #         thread.join()
    #     processVisualizer.join()
           
if __name__ == '__main__':
    app = App()
    # app.mainloop()