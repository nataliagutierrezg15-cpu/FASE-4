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



