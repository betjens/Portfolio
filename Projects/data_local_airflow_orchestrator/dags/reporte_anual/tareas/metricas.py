from airflow.sdk import task


@task
def calcular_kpis(rows):

    total_revenue = 0
    total_items = 0
    products = {}
    categories = {}
    daily_sales = {}

    orders = set()

    for row in rows:

        revenue = row["quantity"] * row["price"]

        total_revenue += revenue
        total_items += row["quantity"]

        orders.add(row["order_id"])

        product = row["product"]

        products[product] = (
            products.get(product, 0)
            + revenue
        )

        category = row["category"]

        categories[category] = (
            categories.get(category, 0)
            + revenue
        )

        date = row["date"]

        daily_sales[date] = (
            daily_sales.get(date, 0)
            + revenue
        )

    total_orders = len(orders)

    average_order_value = (
        total_revenue / total_orders
        if total_orders
        else 0
    )

    top_product = max(
        products,
        key=products.get,
    )

    result = {
        "total_revenue": total_revenue,
        "total_items": total_items,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "top_product": top_product,
        "product_sales": products,
        "category_sales": categories,
        "daily_sales": daily_sales,
    }

    print("KPIs calculados:")
    print(result)

    return result