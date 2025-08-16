from dataclasses import dataclass
from abc import ABC,abstractmethod

@dataclass
class Graphics:
    pass
@dataclass
class Physics:
    pass
@dataclass
class Static:
    pass

@dataclass
class BaseTelemtryData(ABC):
    def __init__(self):
        pass
    def on_launch(self) -> bool:
        pass
    
class ITelemetryReader(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def read(self) -> BaseTelemtryData:
        pass