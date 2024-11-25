LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS orders; */
    CREATE TABLE IF NOT EXISTS orders(
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        id_mp VARCHAR NOT NULL,
        date_reg VARCHAR,
        posting_number VARCHAR NULL,
        company_id INT NULL,
        marketplace_id INT NULL,
        warehouse_id BIGINT NULL,
        packaging_info JSON NULL,
        shipment_date DATE NULL,
        status VARCHAR NOT NULL,
        currency VARCHAR NULL,
        total NUMERIC,
        json_data JSON NULL,
        schema VARCHAR
    );

    /* DROP TABLE IF EXISTS orders_line; */
    CREATE TABLE IF NOT EXISTS orders_line(
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        id_order VARCHAR,
        id_mp BIGINT NOT NULL,
        qnt INT NOT NULL,
        price NUMERIC NOT NULL,
        title VARCHAR,
        json_data JSON NULL
    );
    """,
    """ALTER TABLE IF EXISTS orders add IF NOT EXISTS transfer_to_platform BOOLEAN DEFAULT FALSE;""",
    """
    CREATE INDEX IF NOT EXISTS created_at
    ON orders (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS company_marketplace
    ON orders (company_id, marketplace_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS transfer_to_platform
    ON orders (transfer_to_platform)
    """,
    """
    ALTER TABLE IF EXISTS orders add IF NOT EXISTS transfer_to_platform BOOLEAN DEFAULT FALSE;
    """,
]
