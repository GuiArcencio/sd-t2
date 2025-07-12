import logging
import os

from src.entities.factory import Factory
from src.entities.monitor import run_monitor
from src.entities.store import Store
from src.entities.supplier import Supplier
from src.entities.warehouse import Warehouse

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    entity = os.getenv("ENTITY", "monitor")
    if entity == "supplier":
        Supplier(5000).run()
    elif entity == "warehouse":
        Warehouse(
            supplier_hostname="supplier", supplier_port=5000, storefront_port=5000
        ).run()
    elif entity == "factory1":
        Factory(num_lines=5, supplier_hostname="warehouse", supplier_port=5000).run()
    elif entity == "store":
        Store().run()
    elif entity == "monitor":
        run_monitor()


if __name__ == "__main__":
    main()
