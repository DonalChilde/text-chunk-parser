class App:
    def __init__(self, config, verbosity: int = 0) -> None:
        self.verbosity = verbosity
        self.config = config

    def __repr__(self):
        return f"{self.__class__.__name__}=(verbosity={self.verbosity}, config={self.config})"
