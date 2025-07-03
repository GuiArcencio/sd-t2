import logging

from src.constants import WAREHOUSE_RED_THRESHOLD, WAREHOUSE_YELLOW_THRESHOLD
from src.stock import Stock

logger = logging.getLogger()


class Warehouse:
    _stock: Stock
    _storefront_port: int

    def __init__(
        self, supplier_hostname: str, supplier_port: int, storefront_port: int
    ):
        self._stock = Stock(
            supplier_hostname=supplier_hostname,
            supplier_port=supplier_port,
            yellow_threshold=WAREHOUSE_YELLOW_THRESHOLD,
            red_threshold=WAREHOUSE_RED_THRESHOLD,
        )
        self._storefront_port = storefront_port

    def run(self):
        self._stock.run_storefront(port=self._storefront_port)
        while True:
            quantity_available, status = self._stock.get_quantity()
            if status == "RED":
                quantity_to_request = WAREHOUSE_YELLOW_THRESHOLD - quantity_available

                logger.info(f"Requesting {quantity_to_request} parts from supplier.")
                self._stock.request_supply(quantity_to_request)
