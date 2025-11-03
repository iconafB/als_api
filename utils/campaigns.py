from models.campaign_rules import rules_tbl

def build_dynamic_query(rule:rules_tbl)->tuple[str,dict]:
    print("Print the passed campaign rule")
    print(rule)
    print("rule has been printed")
    base_select_clause="""
        SELECT id,fore_name,last_name,cell 
        FROM info_tbl
        WHERE 1=1
    """
    params={}
    conditions=[]
    #Salary condition

    if rule.salary is not None:
        conditions.append("(salary>=:min_salary OR salary IS NULL)")
        params["min_salary"]=rule.salary
    conditions.append("typedata='Status'")
    #last_used condition

    # 3. last_used
    if rule.last_used is not None:
        conditions.append(
            "(last_used IS NULL OR "
            "DATE_PART('day', NOW()::timestamp - last_used::timestamp) > :last_used_days)"
        )
        params["last_used_days"] = rule.last_used
    # Start birth year range
    if rule.birth_year_start is not None:
        yy=rule.birth_year_start % 100
        conditions.append("CAST(SUBSTRING(id, 1, 2) AS INTEGER) >= :birth_year_start")
        params["birth_year_start"]=yy

    # End birth year upper range 
    if rule.birth_year_end is not None:
        yy=rule.birth_year_end % 100
        conditions.append("CAST(SUBSTRING(id, 1, 2) AS INTEGER) <= :birth_year_end")
        params["birth_year_end"]=yy
    
    # Dynamic Limit
    limit_clause=""
    if rule.limit is not None:
        if rule.limit<=0:
            return None
        limit_clause="LIMIT:limit_count"
        params["limit_count"]=rule.limit
    else:
        limit_clause="LIMIT 2500"
        params["limit_count"]=2500
    #join all the conditions using the AND operator
    #  
    where_clause="AND".join(f"({c})" for c in conditions)

    final_query=f"""
            {base_select_clause}
            AND {where_clause}
            ORDER BY random()
            {limit_clause}
        """.strip()
    
    return final_query,params