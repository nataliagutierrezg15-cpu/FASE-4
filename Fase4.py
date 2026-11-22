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
        self.available = True # Todo servicio nace disponible, se puede desactivar con disable()

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

    def disable(self):
        """Marks the service as not available (it cannot be reserved)."""
        self.available = False
        logging.info(f"Service disabled: {self.service_name}")

    def enable(self):
        """Marks the service as available again."""
        self.available = True
        logging.info(f"Service enabled: {self.service_name}")

    @staticmethod
    def _validate_units(value, unit_name: str, maximum: int):
        """Validates that hours/days are an integer between 1 and the allowed maximum."""
        # isinstance revisa el tipo; bool se excluye porque en Python True/False cuentan como int
        if not isinstance(value, int) or isinstance(value, bool):
            raise ServiceError(f"The number of {unit_name} must be an integer.")
        if value <= 0:
            raise ServiceError(f"The number of {unit_name} must be greater than zero.")
        if value > maximum:
            raise ServiceError(f"The number of {unit_name} cannot exceed {maximum}.")

    def _apply_tax_and_discount(self, subtotal: float, tax_rate: float, discount: float) -> float:
        """Applies tax and discount, checking that the result is consistent."""
        if not isinstance(tax_rate, (int, float)) or not 0 <= tax_rate <= 1:
            raise ServiceError("Tax rate must be a number between 0 and 1.")
        if not isinstance(discount, (int, float)) or discount < 0:
            raise ServiceError("Discount must be a non-negative number.")

        total = subtotal + subtotal * tax_rate  # Suma el impuesto (ej: 0.19 = 19%)
        total -= discount                       # Resta el descuento en pesos

        if total < 0:
            # Un costo negativo no tiene sentido: es un cálculo inconsistente
            raise ServiceError(
                f"Inconsistent cost: discount (${discount:,.2f}) is greater than the total."
            )
        return total

    @abstractmethod
    def validate_parameters(self):
        """Each service validates its own parameters (polymorphism)."""
        pass
    
    @abstractmethod
    def calculate_cost(self, *args, **kwargs) -> float:
        """Polymorphic method to calculate cost."""
        pass

    @abstractmethod
    def describe_service(self) -> str:
        pass

    def get_summary(self) -> str:
        status = "Available" if self.available else "Not available"
        return f"Service: {self.service_name} (Base: ${self.base_cost:,.2f}) - {status}"


# ========================================
# ROOM RESERVATION SERVICE
# ========================================

class RoomReservation(Service):
    """Specialized service for room reservations."""

    MAX_HOURS = 24  # Una sala se puede reservar máximo 24 horas

    def __init__(self, identifier: str, service_name: str, base_cost: float, hours: int):
        super().__init__(identifier, service_name, base_cost)
        self.hours = hours
        self.validate_parameters()  # Si las horas no son válidas, lanza ServiceError

    def validate_parameters(self):
        self._validate_units(self.hours, "hours", self.MAX_HOURS)

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0, units: int = None) -> float:
        """Calculates the cost. Optional 'units' allows charging a different number of hours (overloading)."""
        hours = self.hours if units is None else units
        self._validate_units(hours, "hours", self.MAX_HOURS)
        subtotal = self.base_cost * hours
        return self._apply_tax_and_discount(subtotal, tax_rate, discount)

    def describe_service(self) -> str:
        return f"Room reservation for {self.hours} hour(s)."

# =========================================
# EQUIPMENT RENTAL SERVICE
# =========================================

class EquipmentRental(Service):
    """Specialized service for equipment rental."""

    MAX_DAYS = 30           # Un equipo se alquila máximo 30 días
    INSURANCE_RATE = 0.05   # Seguro obligatorio del 5% sobre el alquiler

    def __init__(self, identifier: str, service_name: str, base_cost: float, days: int):
        super().__init__(identifier, service_name, base_cost)
        self.days = days
        self.validate_parameters()  # Si los días no son válidos, lanza ServiceError

    def validate_parameters(self):
        self._validate_units(self.days, "days", self.MAX_DAYS)

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0, units: int = None) -> float:
        """Calculates the rental cost including equipment insurance."""
        days = self.days if units is None else units
        self._validate_units(days, "days", self.MAX_DAYS)
        subtotal = self.base_cost * days
        subtotal += subtotal * self.INSURANCE_RATE  # Lo propio de este servicio: el seguro
        return self._apply_tax_and_discount(subtotal, tax_rate, discount)

    def describe_service(self) -> str:
        return f"Equipment rental for {self.days} day(s), includes 5% insurance."

# ======================================
# CONSULTING SERVICE
# ======================================
class ConsultingService(Service):
    """Specialized consulting service."""

    MAX_HOURS = 8                 # Una asesoría dura máximo 8 horas
    SPECIALIST_FEE = 20000        # Tarifa fija del especialista por sesión

    def __init__(self, identifier: str, service_name: str, base_cost: float, hours: int):
        super().__init__(identifier, service_name, base_cost)
        self.hours = hours
        self.validate_parameters()  # Si las horas no son válidas, lanza ServiceError

    def validate_parameters(self):
        self._validate_units(self.hours, "hours", self.MAX_HOURS)

    def calculate_cost(self, tax_rate: float = 0, discount: float = 0, units: int = None) -> float:
        """Calculates the consulting cost plus the fixed specialist fee."""
        hours = self.hours if units is None else units
        self._validate_units(hours, "hours", self.MAX_HOURS)
        subtotal = self.base_cost * hours + self.SPECIALIST_FEE  # Lo propio: tarifa fija
        return self._apply_tax_and_discount(subtotal, tax_rate, discount)

    def describe_service(self) -> str:
        return f"Specialized consulting for {self.hours} hour(s) (+ specialist fee)."

# ======================================
# RESERVATION CLASS
# ======================================

class Reservation:
    """Represents a service reservation."""

    def __init__(self, client, service, duration: int):
        if not isinstance(duration, int) or isinstance(duration, bool):
            raise ReservationError("Duration must be an integer.")
        if duration <= 0:
            raise ReservationError("Duration must be greater than zero.")

        self.client = client
        self.service = service
        self.duration = duration
        self.status = "Pending"                          # Toda reserva empieza pendiente
        self.created_at = datetime.datetime.now()        # Fecha y hora en que se creó

    def confirm(self):
        # Operación no permitida: no se confirma algo cancelado o ya confirmado
        if self.status != "Pending":
            raise ReservationError(
                f"Cannot confirm a reservation with status '{self.status}'."
            )
        self.status = "Confirmed"

        logging.info(f"Reservation confirmed for "
                     f"{self.client.name} ")

    def cancel(self):
        # Operación no permitida: no se cancela dos veces
        if self.status == "Cancelled":
            raise ReservationError("The reservation is already cancelled.")
        self.status = "Cancelled"

        logging.info(f"Reservation cancelled for "
                     f"{self.client.name} ")

    def process(self, tax_rate: float = 0, discount: float = 0):
        try:
            # Solo se procesa una reserva pendiente y con el servicio disponible
            if self.status != "Pending":
                raise ReservationError(
                    f"Only pending reservations can be processed (current: '{self.status}')."
                )
            if not self.service.available:
                raise ServiceError(f"Service '{self.service.service_name}' is not available.")

            # Se cobra la duración de la reserva (parámetro opcional 'units')
            total_cost = self.service.calculate_cost(
                tax_rate=tax_rate, discount=discount, units=self.duration
            )

        except Exception as error:
            logging.error(f"Reservation processing failed: {error}")
            # Encadenamiento: el error original queda guardado en __cause__
            raise ReservationError(
                "Error processing reservation."
            ) from error

        else:
            # Solo se ejecuta si el try no tuvo errores
            self.confirm()
            logging.info("Reservation processed successfully.")
            return total_cost

        finally:
            # Se ejecuta SIEMPRE, haya error o no
            logging.info("Reservation processing attempt finished.")

    def get_summary(self) -> str:

        return (f"Reservation | "
                f"Client: {self.client.name} | "
                f"Service: {self.service.service_name} | "
                f"Duration: {self.duration} | "
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

        # No se puede reservar un servicio que no está disponible
        if not service.available:
            raise ServiceError(f"Service '{service.service_name}' is not available.")
            
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

# ==========================================
# INVALID CLIENT DATA TESTS
# ==========================================
# Cada prueba intenta crear un cliente con un dato malo.
# El setter de Client lanza InvalidClientError y el sistema sigue funcionando.
print("\nINVALID CLIENT EMAIL TEST")

try:
    bad_client = Client("C002", "Laura Gomez", "laura.gmail.com", "3001112233")  # Falta la @
except InvalidClientError as e:
    print("Error handled:", e)
    logging.error(f"Invalid client email: {e}")


print("\nINVALID CLIENT NAME TEST")

try:
    bad_client = Client("C003", "Al", "al@gmail.com", "3001112233")  # Nombre muy corto
except InvalidClientError as e:
    print("Error handled:", e)
    logging.error(f"Invalid client name: {e}")


print("\nINVALID CLIENT PHONE TEST")

try:
    bad_client = Client("C004", "Pedro Diaz", "pedro@gmail.com", "300ABC123")  # Tiene letras
except InvalidClientError as e:
    print("Error handled:", e)
    logging.error(f"Invalid client phone: {e}")


# ==========================================
# VALID EQUIPMENT AND CONSULTING SERVICES TEST
# ==========================================
# try / except / else: el else solo se ejecuta si NO hubo error
print("\nVALID EQUIPMENT AND CONSULTING SERVICES TEST")

try:
    service2 = EquipmentRental("S006", "Projector Rental", 30000, 3)
    service3 = ConsultingService("S007", "Software Consulting", 80000, 2)
    system.register_service(service2)
    system.register_service(service3)
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Valid services registration failed: {e}")
else:
    print(service2.describe_service())
    print(service3.describe_service())
    print(system.list_services())


# ==========================================
# INVALID EQUIPMENT DAYS TEST
# ==========================================
print("\nINVALID EQUIPMENT DAYS TEST")

try:
    bad_equipment = EquipmentRental("S008", "Laptop Rental", 40000, -3)  # Días negativos
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Negative equipment days: {e}")


# ==========================================
# INVALID CONSULTING HOURS TESTS
# ==========================================
print("\nNON-INTEGER CONSULTING HOURS TEST")

try:
    bad_consulting = ConsultingService("S009", "Data Consulting", 80000, "abc")  # No es número
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Non-integer consulting hours: {e}")


print("\nCONSULTING HOURS LIMIT TEST")

try:
    bad_consulting = ConsultingService("S010", "Data Consulting", 80000, 9)  # Máximo son 8
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Consulting hours over the limit: {e}")


# ==========================================
# SUCCESSFUL RESERVATION WITH TAX AND DISCOUNT TEST
# ==========================================
# Usa los parámetros opcionales de calculate_cost (variante con impuesto y descuento)
print("\nSUCCESSFUL RESERVATION WITH TAX AND DISCOUNT TEST")

try:
    reservation2 = system.create_reservation("C001", "S006", 3)
    total2 = reservation2.process(tax_rate=0.19, discount=10000)
except SoftwareFJError as e:
    print("Error handled:", e)
    logging.error(f"Equipment reservation failed: {e}")
else:
    print(reservation2.get_summary())
    print(f"Total cost (19% tax, $10,000 discount): ${total2:,.2f}")


# ==========================================
# SERVICE NOT AVAILABLE TEST
# ==========================================
print("\nSERVICE NOT AVAILABLE TEST")

service3.disable()  # La asesoría deja de estar disponible

try:
    system.create_reservation("C001", "S007", 2)
except ServiceError as e:
    print("Error handled:", e)
    logging.error(f"Reservation of unavailable service: {e}")
finally:
    service3.enable()  # finally: se vuelve a activar pase lo que pase


# ==========================================
# INVALID RESERVATION DURATION TEST
# ==========================================
print("\nINVALID RESERVATION DURATION TEST")

try:
    system.create_reservation("C001", "S001", 0)  # Duración cero
except ReservationError as e:
    print("Error handled:", e)
    logging.error(f"Invalid reservation duration: {e}")


# ==========================================
# INCONSISTENT COST TEST (EXCEPTION CHAINING)
# ==========================================
# El descuento es mayor que el total: calculate_cost lanza ServiceError,
# y process() lo encadena dentro de un ReservationError (raise ... from ...)
print("\nINCONSISTENT COST TEST (EXCEPTION CHAINING)")

try:
    reservation3 = system.create_reservation("C001", "S001", 1)
    reservation3.process(discount=999999)
except ReservationError as e:
    print("Error handled:", e)
    print("Original cause:", e.__cause__)  # El error original que causó este
    logging.error(f"Inconsistent cost: {e} | Cause: {e.__cause__}")


# ==========================================
# DOUBLE CANCELLATION TEST
# ==========================================
print("\nDOUBLE CANCELLATION TEST")

try:
    reservation1.cancel()  # reservation1 ya se había cancelado antes
except ReservationError as e:
    print("Error handled:", e)
    logging.error(f"Operation not allowed: {e}")


# ==========================================
# FINAL SYSTEM SUMMARY
# ==========================================
print("\nFINAL SYSTEM SUMMARY")
print("Clients:", system.list_clients())
print("Services:", system.list_services())
print("Reservations:")
for summary in system.list_reservations():
    print(" -", summary)

print("\nThe system finished all simulations without stopping.")
logging.info("All simulations finished. The system remained stable.")
