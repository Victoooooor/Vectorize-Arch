from util.settings import Settings


class VectorizationDriver:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self) -> None:
        raise NotImplementedError