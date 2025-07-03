import os

from src.entities.factory import Factory
from src.entities.supplier import Supplier
from src.entities.warehouse import Warehouse


def main():
    entity = os.getenv("ENTITY", "")
    if entity == "supplier":
        Supplier(5000).run()
    elif entity == "warehouse":
        Warehouse(
            supplier_hostname="supplier", supplier_port=5000, storefront_port=5000
        ).run()
    elif entity == "factory1":
        Factory(num_lines=5, supplier_hostname="warehouse", supplier_port=5000).run()


if __name__ == "__main__":
    main()
