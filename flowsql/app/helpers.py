def deconstruct_sid(column_sid, how):
    if how == "column":
        schema, table = column_sid.split(".")[:2]
        schema_sid = schema
        table_sid = ".".join([schema, table])
        return schema_sid, table_sid, column_sid

    elif how == "table":
        schema, table = table_sid.split(".")
        schema_sid = schema
        table_sid = ".".join([schema, table])
        return schema_sid, table_sid

    else:
        raise Exception("'how' only takes values of 'column' or 'table")
