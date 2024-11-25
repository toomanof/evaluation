SQL_INSERT_ORDERS = (
    "INSERT INTO orders"
    " (id_mp, date_reg, posting_number, "
    "company_id, marketplace_id, warehouse_id, "
    "packaging_info, shipment_date, status, "
    "currency, total, json_data, schema, transfer_to_platform)"
    " VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);"
)
SQL_UPDATE_ORDERS = (
    "UPDATE orders SET  "
    "id_mp=$1, date_reg=$2, posting_number=$3, "
    "company_id=$4, marketplace_id=$5, warehouse_id=$6, "
    "packaging_info=$7, shipment_date=$8, status=$9, "
    "currency=$10, total=$11, json_data=$12, schema=$13, transfer_to_platform=$14"
    " WHERE id_mp=$2 AND company_id=$4 AND marketplace_id=$5;"
)
SQL_SELECT_ORDERS = "SELECT * FROM orders WHERE company_id=$1 AND marketplace_id=$2;"
SQL_SELECT_IDS_ORDERS = "SELECT id_mp FROM orders WHERE company_id=$1 AND marketplace_id=$2;"

SQL_INSERT_ORDER_LINES = (
    "INSERT INTO orders_line" " (id_order, id_mp, qnt, price, title)" " VALUES($1, $2, $3, $4, $5);"
)
SQL_SELECT_ORDER_LINES_MANY_ORDERS = "SELECT * FROM orders_line WHERE id_order in {};"
SQL_SELECT_ORDER_LINE = "SELECT * FROM orders_line WHERE id_order=$1;"
SQL_DELETE_ORDER_LINE = "DELETE FROM orders_line WHERE id_order=ANY($1);"


# Перечислить статусы для определения типа движения
SQL_SELECT_ORDERS_MOVEMENT_DATA = """
    SELECT
        orders_line.title as product_name,
        orders_line.id_mp as product_id,
        COALESCE((orders.json_data->'barcode')::text, (orders.json_data->'skus' ->> 0)::text) as sku,
        orders_line.qnt as value,
		CASE
           WHEN orders.status in ('new', 'confirm', 'complete', 'deliver', 'shipped', 'sorted', 'receive', 'waiting', 'sold', 'ready_for_pickup') THEN '+'
           WHEN orders.status in ('canceled', 'canceled_by_client', 'declined_by_client', 'defect') THEN '-'
        END movement,
        orders_line.id_order,
        orders.warehouse_id as id_warehouse

    FROM public.orders_line
    INNER JOIN orders ON orders_line.id_order = orders.id_mp
"""

SQL_UPDATE_ORDERS_LINE_SENT_DATE = """
UPDATE orders_line
	SET sent_date=$1
	WHERE id = ANY($2);
"""

SQL_UPDATE_ORDERS_TRANSFER = """
UPDATE orders
	SET transfer_to_platform=$1
	WHERE id = ANY($2);
"""
