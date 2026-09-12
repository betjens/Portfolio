from airflow.sdk import task


@task
def depurar_ventas(rows):
    cleaned = []

    for row in rows:
        cleaned.append(
            {
                "date": row["date"],
                "order_id": int(row["order_id"]),
                "product": row["product"].strip(),
                "category": row["category"].strip(),
                "quantity": int(row["quantity"]),
                "price": float(row["price"]),
            }
        )

    print(f"Limpiando {len(cleaned)} registros.")

    return cleaned