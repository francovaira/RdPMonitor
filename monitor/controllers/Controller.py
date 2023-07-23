# from views.Visualizer import Visualizer as view
# from models.JobManager import JobManager as model

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def getMapHorizontalSize(self):
        return self.model.getMapHorizontalSize()
        # self.mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
        # self.mapVerticalSize = map.getMapDefinition().getVerticalSize()

    def getMapVerticalSize(self):
        return self.model.getMapVerticalSize()

    def getMapInSharedMemory(self):
        return self.model.getMapInSharedMemory()

    def start(self):
        try:
            # save the model
            self.model.email = email
            self.model.save()

            # show a success message
            self.view.show_success(f'The email {email} saved!')

        except ValueError as error:
            # show an error message
            self.view.show_error(error)