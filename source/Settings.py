class Settings:

    def __init__(self, channel, era, ml_type="keras", scaler="none"):
        self.channel = channel
        self.era = era
        self.ml_type = ml_type
        self.scaler = scaler
        self.ext_input = False
        self.config_parser = None
        self.filtered_samples = None
        self.model_file_manager = None
        self.prediction_file_manager = None
        self.fraction_plot_file_manager = None
        self.folds = 2
        self.emb = None
        self.varset = None
        self.name = None

    def get_emb_prefix(self):
        emb_prefix = ""
        if self.emb:
            emb_prefix = "emb_"
        return emb_prefix

    def get_emb_suffix(self):
        emb_suffix = ""
        if self.emb:
            emb_suffix = "_emb"
        return emb_suffix

    def __str__(self):
        result = ""
        result += "[Settings: " + "\n"
        result += "ML Type: " + self.ml_type + "\n"
        result += "Channel: " + self.channel + "\n"
        result += "Era: " + self.era + "\n"
        result += "Scaler: " + self.scaler + "]" + "\n"
        return result
