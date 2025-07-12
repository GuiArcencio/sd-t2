import logging
from queue import Queue
from time import sleep

import zmq

from src.constants import (
    ASSEMBLYLINE_RED_THRESHOLD,
    ASSEMBLYLINE_YELLOW_THRESHOLD,
    PRODUCT_DELAYS,
    PRODUCT_DELIVERY_TIME,
    PRODUCT_PARTS,
)
from src.multithreading import delay_thread, launch_thread
from src.stock import Stock

logger = logging.getLogger()


class AssemblyLine:
    _id: str
    _stock: Stock
    _task_queue: Queue
    _store_socket: zmq.Socket

    def __init__(self, id: str, supplier_hostname: str, supplier_port: int):
        context = zmq.Context.instance()

        self._id = id
        self._stock = Stock(
            supplier_hostname=supplier_hostname,
            supplier_port=supplier_port,
            yellow_threshold=ASSEMBLYLINE_YELLOW_THRESHOLD,
            red_threshold=ASSEMBLYLINE_RED_THRESHOLD,
        )
        self._task_queue = Queue()

        self._store_socket = context.socket(zmq.PUSH)
        self._store_socket.connect(f"tcp://store:5000")

    def request(self, item_type: int, quantity: int):
        self._task_queue.put((item_type, quantity))

    def _assembly(self):
        while True:
            item_type, quantity = self._task_queue.get()
            parts_needed = PRODUCT_PARTS[item_type]
            time_needed = PRODUCT_DELAYS[item_type]

            logger.info(
                f"[Line {self._id}] Starting production of {quantity} units of Pv{item_type}"
            )

            for _ in range(quantity):
                parts = self._stock.take(parts_needed)
                while parts < parts_needed:
                    parts += self._stock.take(parts_needed - parts)

                # Work
                sleep(time_needed)

            delay_thread(
                task=self._send_products,
                timeout=PRODUCT_DELIVERY_TIME,
                quantity=quantity,
                item_type=item_type,
            )

            logger.info(
                f"[Line {self._id}] Produced {quantity} items of Pv{item_type}."
            )

    def _send_products(self, quantity: int, item_type: int):
        self._store_socket.send_string(f"{quantity}:{item_type}")

    def run(self):
        launch_thread(self._assembly)
        while True:
            quantity_available, status = self._stock.get_quantity()
            if status == "RED":
                quantity_to_request = ASSEMBLYLINE_YELLOW_THRESHOLD - quantity_available
                logger.info(
                    f"[Line {self._id}] Requesting {quantity_to_request} parts from warehouse."
                )
                self._stock.request_supply(quantity_to_request)
