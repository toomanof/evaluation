SQL_INSERT_STATISTICS = (
    "INSERT INTO statistics"
    " (id_mp, vendor_code, json_data, company_id, marketplace_id, stocks_seller, stocks_market, date_reg)"
    " VALUES($1, $2, $3, $4, $5, $6, $7, $8);"
)
SQL_UPDATE_STATISTICS = (
    "UPDATE statistics SET vendor_code=$2, json_data=$3, stocks_seller=$6, stocks_market=$7, date_reg=$8"
    " WHERE id_mp=$1 AND company_id=$4 AND marketplace_id=$5;"
)
SQL_SELECT_STATISTICS = "SELECT * FROM statistics WHERE company_id=$1 AND marketplace_id=$2;"
SQL_SELECT_STATISTICS_FOR_DATE = "SELECT * FROM statistics WHERE company_id=$1 AND marketplace_id=$2 AND date_reg=$3;"
SQL_SELECT_IDS_STATISTICS = "SELECT id_mp, date_reg FROM statistics WHERE company_id=$1 AND marketplace_id=$2;"

SQL_SELECT_DATES_STATICS = (
    "SELECT DISTINCT (date_reg) FROM statistics " "WHERE company_id=$1 AND marketplace_id=$2 AND date_reg=$3;"
)
