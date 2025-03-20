from abc import ABC, abstractmethod


class PipelineGeneratorBase(ABC):
    @abstractmethod
    def generate_urban_pipeline(self, user_description: str) -> str:
        pass
