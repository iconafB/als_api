INSERT_MANUAL_DEDUPE_QUERY= """
        INSERT INTO campaign_dedupe (id, cell, campaign_name, status, code)
        VALUES (:id, :cell, :campaign_name, :status, :code)
    """
INSERT_MANUAL_DEDUPE_INFO_TBL_QUERY="""
        INSERT INTO info_tbl(cell, extra_info)
        VALUES (:cell, :extra_info)
        ON CONFLICT(cell)
        DO UPDATE SET extra_info = EXCLUDED.extra_info
        WHERE info_tbl.cell = EXCLUDED.cell
    """