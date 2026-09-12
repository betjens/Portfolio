from airflow.sdk import dag
import pendulum

from reporte_anual.tareas.carga import cargar_ventas
from reporte_anual.tareas.depurar import depurar_ventas
from reporte_anual.tareas.metricas import calcular_kpis
from reporte_anual.tareas.charts import generar_charts
from reporte_anual.tareas.report import generar_reporte


@dag(
    dag_id="reporte_anual",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["learning", "reporting"],
)
def reporte_anual():

    ventas = cargar_ventas()

    depurar_datos = depurar_ventas(ventas)

    kpis = calcular_kpis(depurar_datos)

    charts = generar_charts(kpis)

    generar_reporte(kpis, charts)


reporte_anual()