LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS statistics; */
    CREATE TABLE IF NOT EXISTS statistics(
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        id_mp INT NOT NULL,
        vendor_code VARCHAR NOT NULL,
        marketplace_id INT NULL,
        company_id INT NULL,
        json_data JSON NULL,
        date_reg DATE DEFAULT Now(),
        stocks_seller INT,
        stocks_market INT
    );""",
    """
    CREATE INDEX IF NOT EXISTS created_at
    ON statistics (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS company_marketplace
    ON statistics (company_id, marketplace_id)
    """,
]
