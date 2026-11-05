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




