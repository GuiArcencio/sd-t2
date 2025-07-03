from queue import Queue
from time import sleep

from src.constants import (
    ASSEMBLYLINE_RED_THRESHOLD,
    ASSEMBLYLINE_YELLOW_THRESHOLD,
    PRODUCT_DELAYS,
    PRODUCT_PARTS,
)
from src.multithreading import launch_thread
from src.stock import Stock


class AssemblyLine:
    _stock: Stock
    _task_queue: Queue

    def __init__(self, supplier_hostname: str, supplier_port: int):
        self._stock = Stock(
            supplier_hostname=supplier_hostname,
            supplier_port=supplier_port,
            yellow_threshold=ASSEMBLYLINE_YELLOW_THRESHOLD,
            red_threshold=ASSEMBLYLINE_RED_THRESHOLD,
        )
        self._task_queue = Queue()

    def request(self, item_type: int, quantity: int):
        self._task_queue.put((item_type, quantity))

    def _assembly(self):
        while True:
            item_type, quantity = self._task_queue.get()
            for _ in range(quantity):
                parts_needed = PRODUCT_PARTS[item_type]
                time_needed = PRODUCT_DELAYS[item_type]

                parts = self._stock.take(parts_needed)
                while parts < parts_needed:
                    parts += self._stock.take(parts_needed - parts)

                # Work
                sleep(time_needed)

                # TODO: send items somewhere

    def run(self):
        launch_thread(self._assembly)
        while True:
            quantity_available, status = self._stock.get_quantity()
            if status == "RED":
                self._stock.request_supply(
                    ASSEMBLYLINE_YELLOW_THRESHOLD - quantity_available
                )
