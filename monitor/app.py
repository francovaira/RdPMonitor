import multiprocessing
from multiprocessing import Process
from controllers.Controller import Controller
from views.Visualizer import Visualizer
from models.Model import Model
import logging

# class App:
def main():
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        level=logging.DEBUG)
    # create a model
    model = Model()

    # create a view and place it on the root window
    viz = Visualizer(1200, 800)

    # create a controller
    controller = Controller(model, viz)

    # set the controller to view
    viz.setController(controller)
    # cualquier cosa que se ponga despues de esto no se va a ejecutar aunque los hilos terminen
    processVisualizer = multiprocessing.Process(target=viz.run(), daemon=True)
    processVisualizer.run()

if __name__ == '__main__':
    main()
