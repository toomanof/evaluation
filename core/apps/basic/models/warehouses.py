LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS warehouse; */
    CREATE TABLE IF NOT EXISTS warehouse(
        warehouse_id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        title VARCHAR(255),
        marketplace_id INT NULL,
        company_id INT NULL,
        id_mp INT,
        id_shop INT,
        campaign_id VARCHAR(255),
        schema VARCHAR(3),
        attached_platform_warehouse VARCHAR(255),
        json_data JSON NULL
    );""",
    """
    CREATE INDEX IF NOT EXISTS created_at
    ON warehouse (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS company_marketplace
    ON warehouse (company_id, marketplace_id)
    """,
]
