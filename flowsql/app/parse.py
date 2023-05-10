import sqlparse
from sql_metadata import Parser
import json
import os
import logging
import itertools

from flowsql.app.Objects import ObjectCollection


def parse_create_statement(collection: ObjectCollection, statement):
    def get_target_table(statement):
        for line in str(statement).split("\n"):
            if ("CREATE TABLE" in line) and ("AS" in line):
                l = line.split(" ")
                target = l[2]
            elif "INSERT INTO" in line:
                l = line.split(" ")
                target = l[2]

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
                # Add schema and table info to target cols
                target_col = f"{target_schema}.{target_table}.{inv_aliases[source_col]}"
                target_cols.append(target_col)

            else:
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
    parser = Parser(str(statement))

    all_cols, links = get_cols_and_links(
        parser=parser, target_schema=target_schema, target_table=target_table
    )

    for col in all_cols:
        schema, table = col.split(".")[:2]

        schema_sid = schema
        table_sid = ".".join([schema, table])
        column_sid = col

        collection.add_schema(sid=schema_sid)

        collection.add_table(sid=table_sid, schema_sid=schema_sid)

        collection.add_column(sid=column_sid, table_sid=table_sid)

    for link in links:
        source_col_sid = link[0]
        target_col_sid = link[1]

        collection.add_link(
            source_col_sid=source_col_sid, target_col_sid=target_col_sid
        )

    return collection


# def clean(statement):
#     """
#     Clean the statement, returning a list of individual words.

#     Args:
#         statement (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     # # Remove new lines to negate different formats
#     # statement = str(statement).replace('\n', ' ')
#     # # Remove semi-colons as they mark the end of SQL statements
#     # statement = str(statement).replace(';', '')

#     # statement = statement.split(' ')
#     # statement = [s for s in statement if s != '']
#     return statement


def add_to_collection(collection, statements):

    # Looping through all SQL statements in the file, determine what type of statement it is. Add to mapping file accordingly.
    for statement in statements:
        statement_type = statement.get_type()
        # statement = clean(statement)

        if statement_type == "CREATE":
            collection = parse_create_statement(
                collection=collection, statement=statement
            )

        # TODO: Insert other SQL statements here...

    return collection


def main(collection: ObjectCollection, path):

    with open(path, "r") as f:
        raw = f.read()

    statements = sqlparse.parse(raw)

    collection = add_to_collection(collection=collection, statements=statements)

    return collection
