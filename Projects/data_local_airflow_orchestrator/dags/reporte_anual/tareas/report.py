from pathlib import Path

from airflow.sdk import task

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "output"
)

@task
def generar_reporte(kpis, charts):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_file = (
        OUTPUT_DIR
        / "sales_report.html"
    )

    product_rows = ""

    for product, revenue in sorted(
        kpis["product_sales"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        product_rows += f"""
        <tr>
            <td>{product}</td>
            <td>€{revenue:,.2f}</td>
        </tr>
        """

    category_rows = ""

    for category, revenue in sorted(
        kpis["category_sales"].items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        category_rows += f"""
        <tr>
            <td>{category}</td>
            <td>€{revenue:,.2f}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>
            Sales Dashboard
        </title>

        <style>

            body {{
                font-family:
                    Arial,
                    sans-serif;

                background:
                    #f5f7fa;

                margin: 0;
            }}

            .container {{
                max-width: 1100px;
                margin: auto;
                padding: 40px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .subtitle {{
                color: #666;
                margin-bottom: 30px;
            }}

            .metrics {{
                display: grid;

                grid-template-columns:
                    repeat(4, 1fr);

                gap: 20px;

                margin-bottom: 30px;
            }}

            .metric {{
                background: white;

                padding: 22px;

                border-radius: 12px;

                box-shadow:
                    0 2px 8px
                    rgba(0, 0, 0, 0.08);
            }}

            .metric-label {{
                color: #777;
                font-size: 14px;
            }}

            .metric-value {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 8px;
            }}

            .card {{
                background: white;

                padding: 25px;

                margin-bottom: 25px;

                border-radius: 12px;

                box-shadow:
                    0 2px 8px
                    rgba(0, 0, 0, 0.08);
            }}

            .chart {{
                width: 100%;
                max-width: 800px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                text-align: left;
                background: #f0f2f5;
            }}

            td,
            th {{
                padding: 12px;

                border-bottom:
                    1px solid #ddd;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>
                📊 Sales Dashboard
            </h1>

            <div class="subtitle">
                Airflow generated sales report
            </div>


            <div class="metrics">

                <div class="metric">

                    <div class="metric-label">
                        Total Revenue
                    </div>

                    <div class="metric-value">
                        €{kpis["total_revenue"]:,.2f}
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Orders
                    </div>

                    <div class="metric-value">
                        {kpis["total_orders"]}
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Items Sold
                    </div>

                    <div class="metric-value">
                        {kpis["total_items"]}
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Average Order
                    </div>

                    <div class="metric-value">
                        €{kpis["average_order_value"]:,.2f}
                    </div>

                </div>

            </div>


            <div class="card">

                <h2>
                    🏆 Top Product
                </h2>

                <h3>
                    {kpis["top_product"]}
                </h3>

            </div>


            <div class="card">

                <h2>
                    Revenue by Product
                </h2>

                <img
                    class="chart"
                    src="products.png"
                >

            </div>


            <div class="card">

                <h2>
                    Revenue Over Time
                </h2>

                <img
                    class="chart"
                    src="daily_sales.png"
                >

            </div>


            <div class="card">

                <h2>
                    Products
                </h2>

                <table>

                    <tr>
                        <th>Product</th>
                        <th>Revenue</th>
                    </tr>

                    {product_rows}

                </table>

            </div>


            <div class="card">

                <h2>
                    Categories
                </h2>

                <table>

                    <tr>
                        <th>Category</th>
                        <th>Revenue</th>
                    </tr>

                    {category_rows}

                </table>

            </div>


        </div>

    </body>

    </html>
    """

    report_file.write_text(
        html,
        encoding="utf-8",
    )

    print(
        f"Report created: {report_file}"
    )

    return str(report_file)