SQL_INSERT_SALES = (
    "INSERT INTO sales"
    " (id_mp, gnumber, srid, json_data, company_id, marketplace_id)"
    " VALUES($1, $2, $3, $4, $5, $6);"
)
SQL_UPDATE_SALES = (
    "UPDATE sales SET  gnumber=$2, srid=$3, json_data=$4 " " WHERE id_mp=$1 AND company_id=$5 AND marketplace_id=$6;"
)
SQL_SELECT_SALES = "SELECT * FROM sales WHERE company_id=$1 AND marketplace_id=$2;"
SQL_SELECT_IDS_SALES = "SELECT id_mp FROM sales WHERE company_id=$1 AND marketplace_id=$2;"
