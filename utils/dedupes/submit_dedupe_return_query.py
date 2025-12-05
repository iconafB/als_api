
UPDATE_DEDUPE_CAMPAIGN_RETURN_SQL="UPDATE campaign_dedupe SET status = 'R' WHERE code = :code AND id = ANY(:id_list)"
DELETE_LEADS_SQL="DELETE FROM campaign_dedupe WHERE id = ANY(:ids) RETURNING lead_pk"
UPDATE_INFO_TABLE_DEDUPE_SQL="UPDATE info_tbl SET extra_info = NULL WHERE id = ANY(:ids)"
DELETE_CAMPAIGN_DEDUPE_SQL= "DELETE FROM campaign_dedupe WHERE code = :code"

UPDATE_DEDUPE_RETURN_QUERY="""
        UPDATE campaign_dedupe
        SET status = 'R'
        WHERE code = :code
        AND id = ANY(:dedupe_ids)
        RETURNING lead_pk
    """

FECTHING_PENDING_IDS_CAMPAIGN_STATUS_AND_CODE="""
            SELECT id
            FROM campaign_dedupe
            WHERE status = 'P'
            AND code = :code
        """

DELETE_PENDING_IDS_CAMPAIGN_STATUS_AND_CODE="""
            DELETE FROM campaign_dedupe
            WHERE id = ANY(:ids)
            RETURNING lead_pk
        """


UPDATE_PENDING_IDS_ON_THE_INFO_TBL="""
        UPDATE info_tbl
        SET extra_info = NULL
        WHERE id = ANY(:ids)
        RETURNING cell
    """

DELETE_STMT_ON_CAMPAIGN_DEDUPE="""
        DELETE FROM campaign_dedupe
        WHERE code = :u_code
    """