from abc import ABC, asbtractmethod
import logging
import datetime

logging.basicConfig(
    filename='system_software_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    encoding='utf-8'
)

class SoftwareFJError(Exception):
    """Base exception for all errors in the Software FJ system."""
    pass

class InvalidClientError(SoftwareFJError):
    """Raised for errors in client creation or validation."""
    pass

class ServiceError(SoftwareFJError):
    """Raised for errors related to service management."""
    pass

class ReservationError(SoftwareFJError):
    """Raised for errors in the reservation workflow."""
    pass


class AbstractEntity(ABC):
    """Abstract class representing general entities in the system."""
    
    def __init__(self, identifier: str):
        self._identifier = identifier

    @property
    def identifier(self) -> str:
        return self._identifier

    @abstractmethod
    def get_summary(self) -> str:
        pass

class Service(AbstractEntity, ABC):
    def __init__(self, identifier: str, service_name: str, base_cost: float):
        super().__init__(identifier)
        self.service_name = service_name
        self.base_cost = base_cost

    @property
    def base_cost(self) -> float:
        return self.__base_cost

    @base_cost.setter
    def base_cost(self, value: float):
        if value <= 0:
            raise ServiceError("The base cost of the service must be strictly greater than zero.")
        self.__base_cost = float(value)

    @abstractmethod
    def calculate_cost(self, *args, **kwargs) -> float:
        """Polymorphic method to calculate cost."""
        pass

    @abstractmethod
    def describe_service(self) -> str:
        pass

    def get_summary(self) -> str:
        return f"Service: {self.service_name} (Base: ${self.base_cost:,.2f})"
