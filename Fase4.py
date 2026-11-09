from abc import ABC, asbtractmethod
import logging
import datetime

# ==========================================
# LOGGING SYSTEM CONFIGURATION
# ==========================================

logging.basicConfig(
    filename='system_software_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    encoding='utf-8'

# ==========================================
# CUSTOM EXCEPTIONS & EXCEPTION CHAINING
# ==========================================
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

# ==========================================
# GENERAL ABSTRACT CLASS (BASE ENTITY)
# ==========================================
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

# ==========================================
# CLIENT CLASS (Encapsulation & Validations)
# ==========================================
class Client(AbstractEntity):
    def __init__(self, identifier: str, name: str, email: str, phone: str):
        super().__init__(identifier)
        self.name = name
        self.email = email
        self.phone = phone

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if not value or not isinstance(value, str) or len(value.strip()) < 3:
            raise InvalidClientError(f"Invalid client name: '{value}'. Must be at least 3 characters long.")
        self.__name = value.strip()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str):
        if not value or "@" not in value or "." not in value:
            raise InvalidClientError(f"Invalid email address: '{value}'. Required format: user@domain.com")
        self.__email = value.strip()

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, value: str):
        if not value or not value.isdigit() or len(value) < 7:
            raise InvalidClientError(f"Invalid phone number: '{value}'. Must contain digits only and at least 7 characters.")
        self.__phone = value

    def get_summary(self) -> str:
        return f"Client [ID: {self.identifier}] - {self.name} ({self.email})"

# ==========================================
# ABSTRACT SERVICE CLASS
# ==========================================
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


#========================================
# ROOM RESERVATION SERVICE
#========================================

class RoomReservation(Service):
    """Specialized service for room reservations."""

    def __init__(self,identifitier: str, service_name: str, base_cost: float, hours: int):
        super().__init__(identifier, service_name, base_cost)
        self.hours = hours

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost."""

        total = self.base_cost * self.hours
        total += total * tax_rate
        total -= discount

        return total

    def describe_service(self) -> str:
        return f"Room reservation for {self.hours} hour(s)."

#=========================================
#EQUIPMENT RENTAL SERVICE
#=========================================

class EquipmentRental(Service):
    """Specialized service for equipment rental.""""

    def __init__(self, identifier: str, service_name: str, base_cost: float, days: int):
        super.__init__(identifier, service_name, base_cost)

        self.days = days

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost:"""

        total = self.base_cost * self.days
        total += total * tax_rate
        total -= discount

        return total

    def describe_service(self) -> str:
        return f"Equipment rental for {self.days} day(S)."

#======================================
#CONSULTING SERVICE
#======================================

class ConsultingService(Service):
    """Speacilized consulting service."""

    def __init__(self, identifier: str, service_name: str, base_cost: float, hours: init):
        super.__init__(identifier, service_name, base_cost)

        self.hours = hours

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost."""

        total = self.base_cost * self.hours
        total += total * tax_rate
        total -= discount

        return total
    def describe_service(self) -> str:
        return f"Specialized consulting for {self.hours} hour(s)."

#======================================
#RESERVATION CLASS
#======================================

class Reservation:
    """Represents a service reservation."""

    def __init__(self, client, service, duration: int):
        if duration <= 0:
            raise ReservationError("Duration must be greater than zero.")

        self.client = client
        self.service = service
        self.duration = duration
        self.status = "Pending"

    def confirm(self):
        self.status = "Confirmed"

        logging.info(f"Reservation confirmed for "
                     f"{self.client.name} ")

    def cancel(self):
        self.status = "Cancelled"

        logging.info(f"Reservation cancelled for "
                     f"{self.client.name} ")

    def process(self):
        try: 
            total_cost = self.service.calculate_cost()
            self.confirm()
            return total_cost

        except Exceotion as error:
            logging.error(str(error))
            raise ReservationError("Error processing reservation.")
                from error

    def get_summary(self) -> str:

        return (f"Reservation | "
                f"Client: {self.client.name} | "
                f"Service: {self.service.service_name} | "
                f"Status: {self.status}" )
        
        
        





