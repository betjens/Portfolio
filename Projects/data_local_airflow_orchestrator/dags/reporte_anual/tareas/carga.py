import csv
from pathlib import Path

from airflow.sdk import task


DATA_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "ventas_anuales.csv"
)


@task
def cargar_ventas():
    rows = []

    with DATA_FILE.open(newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"Cargado {len(rows)} registros de ventas.")

    return rows