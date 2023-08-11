from abc import ABC, abstractmethod


class AbstractListingFeatureParamsAdapter(ABC):

    @abstractmethod
    def get(self, key: str):
        pass
