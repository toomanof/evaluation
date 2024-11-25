SQL_SELECT_SETTING = "SELECT value FROM settings WHERE code=$1 AND company_id=$2 AND marketplace_id=$3;"
INSERT_SETTING = "INSERT INTO settings (code, value, company_id, marketplace_id) VALUES ($1, $2, $3, $4)"
UPDATE_SETTING = "UPDATE settings SET value=$2 WHERE code=$1 AND company_id=$3 AND marketplace_id=$4;"
