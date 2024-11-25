LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS schema; */
    CREATE TABLE IF NOT EXISTS schema(
        schema_id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        title VARCHAR(5)
    );
    """,
    """
    /* DROP TABLE IF EXISTS settings; */
    CREATE TABLE IF NOT EXISTS settings(
        setting_id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        marketplace_id INT NULL,
        company_id INT NULL,
        code VARCHAR(255),
        value VARCHAR(255)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS created_at
    ON settings (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS company_marketplace
    ON settings (company_id, marketplace_id)
    """,
]
