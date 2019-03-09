from typing import *

class Job:
    contract_id: str
    price: int
    max_clients: int
    expectation: float

    def __init__(self, i, p, k, e):
        self.contract_id = i
        self.price = p
        self.max_clients = k
        self.expectation = e

    def __str__(self):
        return str({
                'id': self.contract_id,
                'p': self.price,
                'k': self.max_clients,
                'e': self.expectation
            })
