from dataclasses import dataclass


@dataclass
class CustomerData:
    customer_id: int
    name: str
    email: str
