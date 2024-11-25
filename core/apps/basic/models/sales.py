LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS sales; */
    CREATE TABLE IF NOT EXISTS sales(
        id_mp VARCHAR NOT NULL,
        created_at TIMESTAMPTZ DEFAULT Now(),
        marketplace_id INT NULL,
        company_id INT NULL,
        gnumber VARCHAR(50) NOT NULL,
        srid VARCHAR NOT NULL,
        json_data JSON NULL
    );""",
    """
    CREATE INDEX IF NOT EXISTS created_at
    ON sales (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS company_marketplace
    ON sales (company_id, marketplace_id)
    """,
]
