import sqlparse
from sql_metadata import Parser

from sqlinks.app.Objects import Collection
from sqlinks.app.helpers import deconstruct_sid


def parse_simple_CTAS_statement(parser, collection: Collection, statement):
    def get_target_table(statement):

        statement = str(statement)
        if ("create table" in statement) and ("as" in statement):
            l = statement.split(" ")
            target = l[2]

        elif "insert into" in statement:
            l = statement.split(" ")
            target = l[2]
        else:
            return None, None

        target_schema, target_table = target.split(".")

        return target_schema, target_table

    def get_cols_and_links(parser, target_schema: str, target_table: str):

        # Source cols =
        #  Any column named in the parser.columns attribute
        source_cols = parser.columns

        # Target cols =
        #  Any column named in the parser.columns attribute (remapped to the target table)
        #  Remapped using the parser.columns_aliases attribute
        #  You must then add again any duplicated source columns that this time DON'T have an alias.
        #
        #  e.g. In this example c.country is picked up as a source column but only once.
        #       Therefore overlaying the parser.columns_aliases will leave us without a "country"
        #       column in the target (only "country_2") unless a corrector function is applied.
        #         SELECT
        #             c.id,
        #             c.name as name,
        #             c.age_int as age,
        #             c.country as country_2,
        #             c.country
        #         FROM spectrum.customers c;

        # Aliases is a lookup of target alias -> source
        aliases = parser.columns_aliases

        # Invert aliases to act as a lookup of source -> target
        inv_aliases = {v: k for k, v in aliases.items()}

        # Create a list of target cols (excl. schema + table)
        # Replaces source col with alias if present, otherwise takes the source col name
        target_cols = []
        links = []
        for source_col in source_cols:
            if source_col in inv_aliases:
                # If a source col is mentioned, and has an alias, then it features in the target table but is renamed
                # Add schema and table info to target cols
                target_col = f"{target_schema}.{target_table}.{inv_aliases[source_col]}"
                target_cols.append(target_col)

            else:
                # If a source col is mentioned, and isn't an alias, then it must feature as a target col with the same name
                # Add schema and table info to target cols
                target_col = (
                    f'{target_schema}.{target_table}.{source_col.split(".")[2]}'
                )
                target_cols.append(target_col)

            # Add links for aliases and non-aliased cols
            links.append([source_col, target_col])

        all_cols = source_cols + target_cols

        return all_cols, links

        # # Corrector function for the above loophole
        # # Works by looping through all the source_cols that are used to create an alias
        # # Then looks through the whole script, picking out lines where the source_col features
        # # Then checks to see that the mention of this source_col, is the LAST mention in the line
        # # (And therefore actually the name of the col being pulled through to the target table)
        # # If so it adds it back to target_cols so it is still captured
        # for col in source_cols_for_alias:
        #     col_name = col.split(".")[-1]
        #     for line in str(statement).split("\n"):
        #         if col_name in line:
        #             split_line = line.replace(".", " ").replace(",", "").split(" ")
        #             res_list = [
        #                 i for i, value in enumerate(split_line) if value == col_name
        #             ]

        #             if len(res_list) != 0:
        #                 if res_list[-1] == len(split_line) - 1:
        #                     target_cols.append(col)

    target_schema, target_table = get_target_table(statement=statement)

    all_cols, links = get_cols_and_links(
        parser=parser, target_schema=target_schema, target_table=target_table
    )

    for column_sid in all_cols:
        schema_sid, table_sid, column_sid = deconstruct_sid(column_sid, how="column")

        collection.add_schema(sid=schema_sid)

        schema = collection.schemas[schema_sid]
        schema.add_table(sid=table_sid, schema_sid=schema_sid)

        table = schema.tables[table_sid]
        table.add_column(sid=column_sid, table_sid=table_sid)

    for link in links:
        source_col_sid = link[0]
        target_col_sid = link[1]

        target_schema_sid, target_table_sid, target_column_sid = deconstruct_sid(
            target_col_sid, how="column"
        )

        column = (
            collection.schemas[target_schema_sid]
            .tables[target_table_sid]
            .columns[target_column_sid]
        )
        column.add_link(source_col_sid=source_col_sid, target_col_sid=target_col_sid)

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

        if statement_type == "UNKNOWN":
            continue

        parser = Parser(str(statement))

        flag_creates_temporary_table = "create temporary table" in str(statement)
        flag_contains_as_select = "as select" in str(statement)

        if statement_type == "CREATE":
            if flag_creates_temporary_table:
                # TODO: Currently doesn't support temporary tables
                continue

            elif len(parser.with_names) == 0 and flag_contains_as_select:
                collection = parse_simple_CTAS_statement(
                    parser=parser, collection=collection, statement=statement
                )

        # TODO: Insert other SQL statements here...

    return collection


def main(collection: Collection, path):

    try:
        with open(path, "r") as f:
            print(path)
            raw = f.read()
    except:
        print(f"WARNING: Encoding failure {path}")
        return collection

    statements = sqlparse.parse(clean(raw))

    collection = add_to_collection(collection=collection, statements=statements)

    return collection
