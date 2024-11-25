SQL_INSERT_WAREHOUSES = (
    "INSERT INTO warehouse" " (title, id_mp, json_data, company_id, marketplace_id)" " VALUES($1, $2, $3, $4, $5);"
)
SQL_UPDATE_WAREHOUSES = (
    "UPDATE warehouse SET  title=$1, json_data=$3" " WHERE id_mp=$2 AND company_id=$4 AND marketplace_id=$5;"
)
SQL_SELECT_WAREHOUSES = "SELECT * FROM warehouse WHERE company_id=$1 AND marketplace_id=$2;"
SQL_SELECT_IDS_WAREHOUSE = "SELECT id_mp FROM warehouse WHERE company_id=$1 AND marketplace_id=$2;"
