from abc import ABC, abstractmethod
import logging
import datetime

# ==========================================
# LOGGING SYSTEM CONFIGURATION
# ==========================================

logging.basicConfig(
    filename='system_software_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    encoding='utf-8',
    force=True)  # Obliga a usar esta configuración aunque Jupyter/Colab ya tenga una

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
        if not isinstance(value, str):
            raise InvalidClientError("Email must be a text value.")

        value = value.strip()

        if (
            not value
            or "@" not in value
            or value.count("@") != 1
            or " " in value
            or "." not in value.split("@")[1]
            or value.split("@")[1].startswith(".")
        ):
            raise InvalidClientError(
                f"Invalid email address: '{value}'. "
                "Required format: user@domain.com"
            )

        self.__email = value

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, value: str):
        if not isinstance(value, str):
            raise InvalidClientError("Phone number must be text.")

        value = value.strip()

        if not value or not value.isdigit() or len(value) < 7:
            raise InvalidClientError(
                f"Invalid phone number: '{value}'. "
                "Must contain digits only and at least 7 characters."
            )

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
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ServiceError("The base cost must be a numeric value.")

        if value <= 0:
            raise ServiceError(
                "The base cost of the service must be strictly greater than zero."
            )

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


# ========================================
# ROOM RESERVATION SERVICE
# ========================================

class RoomReservation(Service):
    """Specialized service for room reservations."""

    def __init__(self, identifier: str, service_name: str, base_cost: float, hours: int):
        super().__init__(identifier, service_name, base_cost)

        if not isinstance(hours, int) or isinstance(hours, bool):
            raise ServiceError("The number of hours must be an integer.")

        if hours <= 0:
            raise ServiceError("The number of hours must be greater than zero.")

        self.hours = hours
    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost."""

        total = self.base_cost * self.hours
        total += total * tax_rate
        total -= discount

        return total

    def describe_service(self) -> str:
        return f"Room reservation for {self.hours} hour(s)."

# =========================================
# EQUIPMENT RENTAL SERVICE
# =========================================

class EquipmentRental(Service):
    """Specialized service for equipment rental."""

    def __init__(self, identifier: str, service_name: str, base_cost: float, days: int):
       super().__init__(identifier, service_name, base_cost)

       self.days = days

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost:"""

        total = self.base_cost * self.days
        total += total * tax_rate
        total -= discount

        return total

    def describe_service(self) -> str:
        return f"Equipment rental for {self.days} day(s)."

# ======================================
# CONSULTING SERVICE
# ======================================
class ConsultingService(Service):
    """Specialized consulting service."""

    def __init__(self, identifier: str, service_name: str, base_cost: float, hours: int):
        super().__init__(identifier, service_name, base_cost)
        self.hours = hours

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0) -> float:
        """Calculates the total service cost."""
        total = self.base_cost * self.hours
        total += total * tax_rate
        total -= discount
        return total

    def describe_service(self) -> str:
        return f"Specialized consulting for {self.hours} hour(s)."

# ======================================
# RESERVATION CLASS
# ======================================

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

        except Exception as error:
            logging.error(str(error))
            raise ReservationError(
                "Error processing reservation."
            ) from error

        else:
            self.confirm()
            logging.info("Reservation processed successfully.")
            return total_cost

        finally:
            logging.info("Reservation processing attempt finished.")
    def get_summary(self) -> str:

        return (f"Reservation | "
                f"Client: {self.client.name} | "
                f"Service: {self.service.service_name} | "
                f"Status: {self.status}" )

      
# ==========================================
# SOFTWARE FJ SYSTEM - SYSTEM MANAGEMENT
# ==========================================

class SoftwareFJSystem:
    """Manages clients, services and reservations."""

    def __init__(self):
        self.clients = []
        self.services = []
        self.reservations = []

    def register_client(self, client):
        if not isinstance(client, Client):
            raise InvalidClientError("Invalid client.")

        if any(c.identifier == client.identifier for c in self.clients):
            raise InvalidClientError("Client already registered.")

        self.clients.append(client)
        logging.info(f"Client registered: {client.name}")

    def register_service(self, service):
        if not isinstance(service, Service):
            raise ServiceError("Invalid service.")

        if any(s.identifier == service.identifier for s in self.services):
            raise ServiceError("Service already registered.")

        self.services.append(service)
        logging.info(f"Service registered: {service.service_name}")

    def create_reservation(self, client_id, service_id, duration):
        client = next(
            (c for c in self.clients if c.identifier == client_id),
            None
        )

        service = next(
            (s for s in self.services if s.identifier == service_id),
            None
        )

        if client is None:
            raise ReservationError("Client not found.")

        if service is None:
            raise ReservationError("Service not found.")

        reservation = Reservation(client, service, duration)
        self.reservations.append(reservation)

        logging.info("Reservation created.")
        return reservation

    def list_clients(self):
        return [client.get_summary() for client in self.clients]
    
    def find_client(self, client_id):
        return next(
            (client for client in self.clients
             if client.identifier == client_id),
            None
        )


    def list_services(self):
        return [service.get_summary() for service in self.services]
    
    def find_service(self, service_id):
        return next(
            (service for service in self.services
             if service.identifier == service_id),
            None
        )


    def list_reservations(self):
        return [reservation.get_summary()
                for reservation in self.reservations]
  


# ==========================================
# INITIAL SYSTEM TEST
# ==========================================

system = SoftwareFJSystem()

client1 = Client(
    "C001",
    "Carlos Perez",
    "carlos@gmail.com",
    "3001234567"
)

system.register_client(client1)

print("CLIENT REGISTRATION TEST")
print(system.list_clients())
      

        
# ==========================================
# SERVICE REGISTRATION TEST
# ==========================================

service1 = RoomReservation(
    "S001",
    "Meeting Room",
    50000,
    2
)

system.register_service(service1)

print("\nSERVICE REGISTRATION TEST")
print(system.list_services())



# ==========================================
# RESERVATION CREATION TEST
# ==========================================

reservation1 = system.create_reservation(
    "C001",
    "S001",
    2
)

print("\nRESERVATION CREATION TEST")
print(system.list_reservations())



# ==========================================
# RESERVATION PROCESSING TEST
# ==========================================

total = reservation1.process()

print("\nRESERVATION PROCESSING TEST")
print("Reservation status:", reservation1.status)
print("Total cost: $", total)



# ==========================================
# RESERVATION CANCELLATION TEST
# ==========================================

reservation1.cancel()

print("\nRESERVATION CANCELLATION TEST")
print("Reservation status:", reservation1.status)



# ==========================================
# CLIENT SEARCH TEST
# ==========================================

found_client = system.find_client("C001")

print("\nCLIENT SEARCH TEST")
print(found_client.get_summary() if found_client else "Client not found")



# ==========================================
# SERVICE SEARCH TEST
# ==========================================

found_service = system.find_service("S001")

print("\nSERVICE SEARCH TEST")
print(found_service.get_summary() if found_service else "Service not found")



# ==========================================
# RESERVATION LIST TEST
# ==========================================

print("\nRESERVATION LIST TEST")
print(system.list_reservations())


# ==========================================
# INVALID CLIENT TEST
# ==========================================

print("\nINVALID CLIENT TEST")

try:
    system.create_reservation("C999", "S001", 2)
except ReservationError as e:
    print("Error handled:", e)
    logging.error(f"Reservation with unknown client: {e}")  # Registra el error en el archivo de logs

# ==========================================
# DUPLICATE CLIENT TEST
# ==========================================

print("\nDUPLICATE CLIENT TEST")

try:
    system.register_client(client1)
except InvalidClientError as e:
    print("Error handled:", e)
    logging.error(f"Duplicate client registration: {e}") # Registra el error en el archivo de logs


# ==========================================
# INVALID SERVICE COST TEST
# ==========================================
print("\nINVALID SERVICE COST TEST")

try:
    invalid_service = RoomReservation(
        "S002",
        "Invalid Room",
        -50000,
        2
    )
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Negative service cost: {e}")  # Registra el error en el archivo de logs

# ==========================================
# NON-NUMERIC SERVICE COST TEST
# ==========================================
print("\nNON-NUMERIC SERVICE COST TEST")

try:
    invalid_service = RoomReservation(
        "S003",
        "Invalid Room",
        "abc",
        2
    )
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Non-numeric service cost: {e}")  # Registra el error en el archivo de logs


    # ==========================================
# INVALID ROOM HOURS TEST
# ==========================================
print("\nINVALID ROOM HOURS TEST")

try:
    invalid_room = RoomReservation(
        "S004",
        "Invalid Room",
        50000,
        -2
    )
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Negative room hours: {e}")  # Registra el error en el archivo de logs

# ==========================================
# NON-INTEGER ROOM HOURS TEST
# ==========================================
print("\nNON-INTEGER ROOM HOURS TEST")

try:
    invalid_room = RoomReservation(
        "S005",
        "Invalid Room",
        50000,
        "abc"
    )
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Non-integer room hours: {e}")  # Registra el error en el archivo de logs
