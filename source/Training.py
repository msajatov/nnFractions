from TrainingDataHandler import TrainingDataHandler
from DataController import DataController


class Training:

    def __init__(self, settings, file_manager, parser, sample_sets):
        self.settings = settings
        self.file_manager = file_manager
        self.parser = parser
        self.sample_sets = sample_sets
        self.model = 0
        self.scaler = 0
        self.setup()

    def setup(self):
        pass

    def train(self):
        training_handler = TrainingDataHandler(self.settings, self.file_manager, self.parser, 0, 0)
        controller = DataController(self.parser.data_root_path, 2, self.parser, self.settings, sample_sets=[])

        sample_info_dicts = controller.prepare(self.sample_sets)
        training_folds = controller.read_for_training(sample_info_dicts)

        training_handler.handle(training_folds)
