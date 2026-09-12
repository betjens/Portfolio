from airflow.sdk import dag, task
import pendulum
import csv
from airflow.providers.smtp.operators.smtp import EmailOperator

CSV_FILE = "/home/betjens/airflow/data/ventas.csv"


@dag(
    dag_id="reporte_ventas",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["learning", "etl"],
)
def daily_sales_report():

    @task
    def extract():
        rows = []

        with open(CSV_FILE, newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                rows.append(row)

        print(f"Loaded {len(rows)} rows")

        return rows

    @task
    def transform(rows):
        total_revenue = 0
        total_items = 0
        product_sales = {}

        for row in rows:
            quantity = int(row["quantity"])
            price = float(row["price"])

            revenue = quantity * price

            total_revenue += revenue
            total_items += quantity

            product = row["product"]

            product_sales[product] = (
                product_sales.get(product, 0) + revenue
            )

        result = {
            "total_revenue": total_revenue,
            "total_items": total_items,
            "product_sales": product_sales,
        }

        print(result)

        return result

    @task
    def generate_report(data):

        products = ""

        for product, revenue in data["product_sales"].items():
            products += f"""
            <tr>
                <td>{product}</td>
                <td>€{revenue:,.2f}</td>
            </tr>
            """

        html = f"""
        <html>
            <body>

                <h1>Daily Sales Report</h1>

                <h2>Summary</h2>

                <p>
                    <strong>Total revenue:</strong>
                    €{data["total_revenue"]:,.2f}
                </p>

                <p>
                    <strong>Items sold:</strong>
                    {data["total_items"]}
                </p>

                <h2>Sales by product</h2>

                <table border="1" cellpadding="8">

                    <tr>
                        <th>Product</th>
                        <th>Revenue</th>
                    </tr>

                    {products}

                </table>

            </body>
        </html>
        """

        return html

    rows = extract()

    transformed = transform(rows)

    generate_report(transformed)


daily_sales_report()