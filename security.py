from sqlglot import parse_one, exp

def is_dangerous(sql):
    if sql == "NOT_DB_QUESTION":
        return False

    try:
        parsed = parse_one(sql)

        # only allow SELECT queries
        if not isinstance(parsed, exp.Select):
            return True

        # allow only uploaded_data table
        allowed_tables = {"uploaded_data", "customers"}

        for table in parsed.find_all(exp.Table):
            if table.name.lower() not in allowed_tables:
                return True

        # detect tautologies like 1=1
        for condition in parsed.find_all(exp.EQ):

            left = condition.left
            right = condition.right

            if (
                    isinstance(left, exp.Literal)
                    and isinstance(right, exp.Literal)
            ):

                if left.this == right.this:
                    return True

        return False

    except:
        return True