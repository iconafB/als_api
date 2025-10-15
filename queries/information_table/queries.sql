

fetch_leads_query=SELECT id, fore_name, last_name, cell FROM info_tbl WHERE (salary>=16000 or salary is null) and (typedata = "Status") and (last_used is null or (DATE_PART("day",now()::timestamp - last_used::timestamp) > 29)) and (CAST(SUBSTRING(id,1,2) AS INTEGER) <=98 and CAST(SUBSTRING(id,1,2) AS INTEGER) >=68) order by random() limit 2500