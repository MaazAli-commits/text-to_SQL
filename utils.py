def add_limit(sql):
    if "limit" not in sql.lower():
        sql = sql.rstrip(";") + " LIMIT 100"
    return sql