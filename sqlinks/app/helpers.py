def deconstruct_sid(sid, how):
    if how == "column":
        schema, table = sid.split(".")[:2]
        schema_sid = schema
        table_sid = ".".join([schema, table])
        column_sid = sid
        return schema_sid, table_sid, column_sid

    elif how == "table":
        # For handling [schema.table] table references
        if sid.count(".") == 1:
            schema, table = sid.split(".")
            schema_sid = schema
            table_sid = ".".join([schema, table])
            return schema_sid, table_sid

        # For hanlding [db.schema.table] table references
        elif sid.count(".") == 2:
            db, schema, table = sid.split(".")
            schema_sid = ".".join([db, schema])
            table_sid = sid
            return schema_sid, table_sid

    else:
        raise Exception("'how' only takes values of 'column' or 'table")


def clean_sid(sid):
    sid = sid.replace("[", "")
    sid = sid.replace("]", "")
    sid = sid.replace("'", "")
    sid = sid.replace('"', "")
    return sid
