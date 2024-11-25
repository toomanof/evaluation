SQL_INSERT_STOCKS = (
    "INSERT INTO register_stock"
    " (id_mp, vendor_code, json_data, company_id, marketplace_id, stocks_mp, stocks_wb)"
    " VALUES($1, $2, $3, $4, $5, $6, $7);"
)
SQL_UPDATE_STOCKS = (
    "UPDATE register_stock SET vendor_code=$2, json_data=$3, stocks_mp=$6, stocks_wb=$7"
    " WHERE id_mp=$1 AND company_id=$4 AND marketplace_id=$5;"
)
SQL_SELECT_STOCKS = "SELECT * FROM register_stock" " WHERE company_id=$1 AND marketplace_id=$2;"
SQL_SELECT_IDS_STOCKS = "SELECT id_mp FROM register_stock" " WHERE company_id=$1 AND marketplace_id=$2;"
