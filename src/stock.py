from time import sleep

import zmq

from src.constants import STOREFRONT_PER_ITEM_SENT_DELAY
from src.multithreading import AtomicValue, launch_thread


class Stock:
    """
    General stock/buffer class for parts or products.
    """

    _yellow_threshold: int
    _red_threshold: int
    _supplier_socket: zmq.Socket
    _storefront_socket: zmq.Socket

    _quantity: AtomicValue[int]

    def __init__(
        self,
        supplier_hostname: str,
        supplier_port: int,
        yellow_threshold: int,
        red_threshold: int,
    ):
        context = zmq.Context.instance()

        self._yellow_threshold = yellow_threshold
        self._red_threshold = red_threshold

        self._supplier_socket = context.socket(zmq.REQ)
        self._supplier_socket.connect(f"tcp://{supplier_hostname}:{supplier_port}")

        self._quantity = AtomicValue(0)

    def get_quantity(self) -> tuple[int, str]:
        current_quantity = self._quantity.get()

        if current_quantity <= self._red_threshold:
            status = "RED"
        elif current_quantity <= self._yellow_threshold:
            status = "YELLOW"
        else:
            status = "GREEN"

        return current_quantity, status

    def take(self, quantity: int) -> int:
        return self._quantity.update(lambda q: q - min(quantity, q))

    def add(self, quantity: int):
        self._quantity.update(lambda q: q + quantity)

    def request_supply(self, quantity: int):
        self._supplier_socket.send_string(str(quantity))
        quantity_received = int(self._supplier_socket.recv_string())
        self.add(quantity_received)

    def run_storefront(self, port: int):
        """
        Allow other services to consume from this stock
        """
        launch_thread(self._run_storefront, port)

    def _run_storefront(self, port: int):
        context = zmq.Context.instance()
        self._storefront_socket = context.socket(zmq.REP)
        self._storefront_socket.bind(f"tcp://*:{port}")

        while True:
            quantity_requested = int(self._storefront_socket.recv_string())
            quantity_to_send = self.take(quantity_requested)
            sleep(STOREFRONT_PER_ITEM_SENT_DELAY * quantity_to_send)
            self._storefront_socket.send_string(str(quantity_to_send))
