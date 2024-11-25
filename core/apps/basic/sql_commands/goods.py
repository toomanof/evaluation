SQL_INSERT_INFO_GOODS = (
    "INSERT INTO product_info "
    "(marketplace_id, company_id, product_id, offer_id, sku, json_data) "
    "VALUES(NULL, NULL, $1, $2, $3, $4);"
)
SQL_UPDATE_INFO_GOODS = "UPDATE product_info SET  offer_id=$2, sku=$3, json_data=$4 WHERE product_id=$1"
SQL_SELECT_PRODUCT_ID_FROM_INFO_GOODS = "SELECT product_id FROM product_info;"


SQL_INSERT_ATTR_GOODS = (
    "INSERT INTO product_attr "
    "(marketplace_id, company_id, product_id, offer_id, json_data) "
    "VALUES(NULL, NULL, $1, $2, $3);"
)
SQL_UPDATE_ATTR_GOODS = "UPDATE product_attr SET  offer_id=$2, json_data=$3 WHERE product_id=$1"
SQL_SELECT_PRODUCT_ID_FROM_ATTR_GOODS = "SELECT product_id FROM product_attr;"


SQL_INSERT_STOCK_GOODS = (
    "INSERT INTO register_stock "
    "(marketplace_id, company_id, product_id, offer_id, present, reserved, type) "
    "VALUES(NULL, NULL, $1, $2, $3, $4, $5);"
)
SQL_UPDATE_STOCK_GOODS = "UPDATE register_stock SET  offer_id=$2, present=$3, reserved=$4, type=$5 WHERE product_id=$1"
SQL_SELECT_PRODUCT_ID_FROM_STOCK_GOODS = "SELECT product_id FROM register_stock;"
