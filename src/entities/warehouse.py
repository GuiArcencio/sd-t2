import logging

import zmq

from src.constants import WAREHOUSE_RED_THRESHOLD, WAREHOUSE_YELLOW_THRESHOLD
from src.multithreading import launch_thread
from src.stock import Stock

logger = logging.getLogger()


class Warehouse:
    _stock: Stock
    _storefront_port: int
    _monitor_socket: zmq.Socket

    def __init__(
        self, supplier_hostname: str, supplier_port: int, storefront_port: int
    ):
        context = zmq.Context.instance()

        self._stock = Stock(
            supplier_hostname=supplier_hostname,
            supplier_port=supplier_port,
            yellow_threshold=WAREHOUSE_YELLOW_THRESHOLD,
            red_threshold=WAREHOUSE_RED_THRESHOLD,
        )
        self._storefront_port = storefront_port

        self._monitor_socket = context.socket(zmq.REP)
        self._monitor_socket.bind("tcp://*:6000")

    def run(self):
        self._stock.run_storefront(port=self._storefront_port)
        launch_thread(task=self.monitor_thread)
        while True:
            quantity_available, status = self._stock.get_quantity()

            if status == "RED":
                quantity_to_request = WAREHOUSE_YELLOW_THRESHOLD - quantity_available

                logger.info(f"Requesting {quantity_to_request} parts from supplier.")
                self._stock.request_supply(quantity_to_request)

    def monitor_thread(self):
        while True:
            _ = self._monitor_socket.recv()
            quantity_available, status = self._stock.get_quantity()
            self._monitor_socket.send_string(f"{quantity_available}:{status}")
