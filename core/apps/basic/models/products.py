LIST_SQL_CREATE_TABLES = [
    """
    /* DROP TABLE IF EXISTS product_info; */
    CREATE TABLE IF NOT EXISTS product_info(
        p_id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        marketplace_id INT NULL,
        company_id INT NULL,
        product_id INT UNIQUE NOT NULL,
        offer_id VARCHAR NOT NULL,
        sku INT NOT NULL,
        json_data JSON NULL
    );""",
    """
    /* DROP TABLE IF EXISTS product_attr; */
    CREATE TABLE IF NOT EXISTS product_attr(
        product_attr_id SERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ DEFAULT Now(),
        marketplace_id INT NULL,
        company_id INT NULL,
        product_id INT UNIQUE NOT NULL,
        offer_id VARCHAR NOT NULL,
        json_data JSON NULL
    );""",
]
