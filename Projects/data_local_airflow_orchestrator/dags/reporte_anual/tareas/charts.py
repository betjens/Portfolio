# install matplotlib in your virtual environment:  pip install matplotlib

from pathlib import Path

import matplotlib.pyplot as plt

from airflow.sdk import task

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "output"
)

@task
def generar_charts(kpis):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    product_chart = OUTPUT_DIR / "products.png"
    daily_chart = OUTPUT_DIR / "daily_sales.png"

    # -------------------------
    # Product revenue
    # -------------------------

    products = list(
        kpis["product_sales"].keys()
    )

    revenues = list(
        kpis["product_sales"].values()
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        products,
        revenues,
    )

    plt.title(
        "Revenue by Product"
    )

    plt.ylabel(
        "Revenue (€)"
    )

    plt.tight_layout()

    plt.savefig(product_chart)

    plt.close()

    # -------------------------
    # Daily revenue
    # -------------------------

    dates = list(
        kpis["daily_sales"].keys()
    )

    daily_revenue = list(
        kpis["daily_sales"].values()
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        dates,
        daily_revenue,
        marker="o",
    )

    plt.title(
        "Daily Revenue"
    )

    plt.ylabel(
        "Revenue (€)"
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(daily_chart)

    plt.close()

    print(
        f"Charts created in {OUTPUT_DIR}"
    )

    return {
        "product_chart": str(product_chart),
        "daily_chart": str(daily_chart),
    }