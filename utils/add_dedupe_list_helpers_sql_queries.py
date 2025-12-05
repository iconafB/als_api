INSERT_INTO_CAMPAIGN_DEDUPE_TABLE_QUERY="INSERT INTO campaign_dedupe(id, cell, campaign_name, status, code) VALUES (%s, %s, %s, %s, %s)"
INSERT_INTO_INFO_TABLE_QUERY="INSERT INTO info_tbl(cell, extra_info) VALUES (%s, %s) ON CONFLICT(cell) DO UPDATE SET extra_info = EXCLUDED.extra_info WHERE info_tbl.cell = EXCLUDED.cell"
