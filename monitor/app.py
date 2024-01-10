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

        # view = View(self)
        # view.grid(row=0, column=0, padx=10, pady=10)

        # create a controller
        controller = Controller(model, viz)

        # set the controller to view
        viz.setController(controller)
        # cualquier cosa que se ponga despues de esto no se va a ejecutar aunque los hilos terminen
        processVisualizer = multiprocessing.Process(target=viz.run(), daemon=True)
        processVisualizer.start()

if __name__ == '__main__':
    app = App()
