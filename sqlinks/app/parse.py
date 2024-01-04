import sqlparse
from sql_metadata import Parser
from sqlinks.app.Objects import Collection


def parse_statement(parser, collection: Collection, statement, statement_type: str):
    statement = str(statement)

    if statement_type == "CTAS":
        l = statement.split(" ")
        if l[0] == "create" and l[1] == "table" and l[3] == "as":
            target_table_sid = l[2]

    elif statement_type == "SELECT_INTO":
        if "into" in statement:
            l = [l for l in statement.split(" ") if l != ""]
            target_table_sid = l[l.index("into") + 1]

    # TODO: Fix the below
    # Currently just skipping any instances where no tables are picked up.
    # They should be picked up, but aren't
    try:
        tables = parser.tables
    except:
        print("Failed to load parser.tables. Skipping statement.")
        return collection

    # Create a table object for every table sid that's found
    # Create a link object for every table sid that's found (with the exception of the target_table_sid)
    for table_sid in parser.tables:
        collection.add_table(sid=table_sid)

        if table_sid != target_table_sid:
            collection.add_link(
                source_table_sid=table_sid, target_table_sid=target_table_sid
            )

    return collection


def clean(raw):
    """
    Clean the statement, returning a list of individual words.

    Args:
        statement (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Remove new lines to negate different formats
    clean = str(raw).lower()
    clean = clean.replace("\n", " ")
    clean = clean.replace("\t", " ")

    # statement = statement.split(' ')
    # statement = [s for s in statement if s != '']
    return clean


def add_to_collection(collection, statements):
    # Looping through all SQL statements in the file, determine what type of statement it is. Add to mapping file accordingly.
    for statement in statements:
        statement_type = statement.get_type()

        if statement_type in ["UNKNOWN", "DROP"]:
            continue
        else:
            parser = Parser(str(statement))

        # Ignore temporary tables
        # TODO: Create functionality to parse temporary tables
        if "create temporary table" in str(statement):
            continue

        # Ignore unpivot statements
        # TODO: Create functionality to parse unpivots
        elif "unpivot" in str(statement):
            continue

        # Parse CTAS statements
        elif statement_type == "CREATE" and "as select" in str(statement):
            collection = parse_statement(
                parser=parser,
                collection=collection,
                statement=statement,
                statement_type="CTAS",
            )

        # Parse SELECT INTO statements
        elif statement_type == "SELECT" and "into" in str(statement):
            collection = parse_statement(
                parser=parser,
                collection=collection,
                statement=statement,
                statement_type="SELECT_INTO",
            )

    return collection


def main(collection: Collection, path):
    try:
        with open(path, "r") as f:
            raw = f.read()
    except:
        print(f"WARNING: Encoding failure {path}")
        return collection

    statements = sqlparse.parse(clean(raw))

    collection = add_to_collection(collection=collection, statements=statements)

    return collection
