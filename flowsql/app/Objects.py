import pprint


class Object:
    object_counter = 1000

    def __init__(self, sid):
        # String ID
        self.sid = sid
        # Numerical ID
        self.nid = Object.object_counter
        Object.object_counter += 1


class Schema(Object):
    def __init__(self, sid: str):
        Object.__init__(self, sid)
        self.name = sid


class Table(Object):
    def __init__(self, sid: str, schema_sid: str):
        Object.__init__(self, sid)
        self.schema_sid = schema_sid
        self.name = sid.split(".")[1]
        self.max_text_length = len(self.name)
        self.num_columns = 0
        self.num_children = 0
        self.num_parents = 0


class Column(Object):
    def __init__(self, sid: str, table_sid: str):
        Object.__init__(self, sid)
        self.table_sid = table_sid
        self.name = sid.split(".")[2]


class Link(Object):
    def __init__(self, source_col_sid: str, target_col_sid: str):
        Object.__init__(self, sid=None)
        self.source_sid = source_col_sid
        self.target_sid = target_col_sid


class ObjectCollection:
    def __init__(self):
        self._schemas = {}

        # Schema lookup. The key (schema_sid) returns a list of tables (table_sids).
        self._schema_tables_lookup = {}
        self._tables = {}
        self._table_columns_lookup = {}
        self._columns = {}
        # Target columns mapping to links
        self._column_links_lookup = {}
        self._links = {}

    def add_schema(self, sid: str):
        print(sid, self._schema_tables_lookup)
        if sid in self._schema_tables_lookup:
            return
        new_schema = Schema(sid=sid)
        self._schemas[sid] = new_schema
        self._schema_tables_lookup[sid] = []

    def add_table(self, sid: str, schema_sid: int):
        if sid in self._table_columns_lookup:
            return
        new_table = Table(sid=sid, schema_sid=schema_sid)
        self._tables[sid] = new_table

        # Append table sid to the schema->tables lookup
        self._schema_tables_lookup[schema_sid].append(sid)
        # Create empty table->cols lookup
        self._table_columns_lookup[sid] = []

    def add_column(self, sid: str, table_sid: int):
        if sid in self._column_links_lookup:
            return
        new_column = Column(sid=sid, table_sid=table_sid)
        self._columns[sid] = new_column

        self._tables[table_sid].num_columns += 1

        column_name_len = len(sid.split(".")[2])
        if column_name_len > self._tables[table_sid].max_text_length:
            self._tables[table_sid].max_text_length = column_name_len

        # Append column sid to the table->columns lookup
        self._table_columns_lookup[table_sid].append(sid)
        # Create empty col->links lookup
        self._column_links_lookup[sid] = []

    def add_link(self, source_col_sid: int, target_col_sid: int):
        new_link = Link(source_col_sid=source_col_sid, target_col_sid=target_col_sid)
        self._links[new_link.nid] = new_link

        # Append link sid to the target_col->links lookup
        self._column_links_lookup[target_col_sid].append(new_link.nid)

        # Increment num_parents and num_children accordingly
        source_table_sid = self._columns[source_col_sid].table_sid
        target_table_sid = self._columns[target_col_sid].table_sid

        self._tables[source_table_sid].num_children += 1
        self._tables[target_table_sid].num_parents += 1

    def print_snapshot(self, how="pretty"):
        def pretty_print_snapshot(snapshot=self.snapshot):

            line_breaks = 3
            schema_offset = 2
            table_offset = 3
            whole_line = 100
            column_width = (whole_line - table_offset) // 2

            def print_line(type=None, text="", source_sid=None, target_sid=None):

                if type == "schema":
                    print("\n" * line_breaks)
                    print(" " * schema_offset + "#" * whole_line)
                    buffer = 3
                    offset = len(text) // 2
                    print(" " * schema_offset + " " * (column_width - offset) + text)
                    print(" " * schema_offset + "#" * whole_line)

                elif type == "table":
                    print()
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")
                    offset = len(text) // 2
                    print(
                        " " * table_offset
                        + "|"
                        + " " * (column_width - offset)
                        + text
                        + " " * (column_width - (len(text) - offset))
                        + "|"
                    )
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")

                elif type == "link":
                    print(
                        " " * table_offset
                        + "|"
                        + source_sid
                        + " " * (column_width - len(source_sid) - 2)
                        + "->"
                        + " " * (column_width - len(target_sid))
                        + target_sid
                        + "|"
                    )
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")

            for schema in snapshot:
                schema_sid = schema["name"]
                print_line(type="schema", text=schema_sid)

                for table in schema["tables"]:
                    table_sid = table["name"]
                    print_line(type="table", text=table_sid)

                    for column in table["cols"]:
                        column_sid = column["name"]

                        links = column["links"]

                        if links == []:
                            print_line(
                                type="link", source_sid="", target_sid=column_sid
                            )

                        else:
                            for link in links:
                                print_line(
                                    type="link",
                                    source_sid=self._links[link["link_id"]].source_sid,
                                    target_sid=self._links[link["link_id"]].target_sid,
                                )

            print("\n" * line_breaks)

        if how == "raw":
            pprint.pprint(self.snapshot)
        elif how == "pretty":
            pretty_print_snapshot()

    def create_snapshot(self):
        """
        snapshot is the desired end state. This is what is used as an input to Jinja to create the
        draw.io diagram.
        snapshot = [
            {
                'name':'stage.reference_rts',
                'id':3,
                'x':900,
                'cols':[
                    {
                        'name':'region',
                        'id':301,
                        'y':26,
                        'links':[]
                    },
                    {
                        'name':'county',
                        'id':302,
                        'y':52,
                        'links':[{
                                'link_id':900,
                                'parent_id':402
                            }]
                    },
                    {
                        'name':'indoor_outdoor',
                        'id':303,
                        'y':78,
                        'links':[]
                    }
                ]
            },
            {
                'name':'reporting.reference_postcode',
                'id':4,
                'x': 300,
                'cols':[
                    {
                        'name':'region_name',
                        'id':401,
                        'y':26,
                        'links':[]
                    },
                    {
                        'name':'county_name',
                        'id':402,
                        'y':52,
                        'links':[]
                    }
                ]
            }
        ]
        """

        def determine_table_ordering():
            # order tables and links
            ordering_dict = {}
            for table_sid, table in self._tables.items():
                ordering_dict[table_sid] = {
                    "net_parent": table.num_parents - table.num_children
                }

            # sort by no. parents, then no. children; note the lambda uses a tuple
            order = 0
            for table_sid in sorted(
                ordering_dict,
                key=lambda k: (ordering_dict[k]["net_parent"]),
            ):
                self._tables[table_sid].order = order
                order += 1

        def create_snapshot():
            snapshot = []
            x_delta = 400
            y_delta = 150
            row_height = 26
            width_per_text_length = 8

            num_per_column = 2

            for schema_sid, table_sids in self._schema_tables_lookup.items():
                schema = self._schemas[schema_sid]
                schema_snapshot = {
                    "name": schema.sid,
                    "id": schema.nid,
                    "x": 0,
                    "y": 0,
                    "height": 100,
                    "width": 100,
                    "tables": [],
                }

                for table_sid in table_sids:

                    table = self._tables[table_sid]
                    table_snapshot = {
                        "name": table.name,
                        "id": table.nid,
                        "order": table.order,
                        "height": (table.num_columns + 1) * row_height,
                        "width": table.max_text_length * width_per_text_length,
                        "x": x_delta + ((table.order // num_per_column) * x_delta),
                        "y": y_delta + ((table.order % num_per_column) * y_delta),
                        "cols": [],
                    }

                    column_counter = 1
                    link_counter = 1

                    for column_sid in self._table_columns_lookup[table_sid]:

                        column = self._columns[column_sid]
                        column_snapshot = {
                            "name": column.name,
                            "id": column.nid,
                            "width": table_snapshot["width"],
                            "height": row_height,
                            "y": column_counter * row_height,
                            "links": [],
                        }

                        link_nids = self._column_links_lookup[column_sid]
                        for link_nid in link_nids:
                            link = self._links[link_nid]
                            link_snapshot = {
                                "link_id": link_nid,
                                "parent_id": self._columns[link.source_sid].nid,
                                "mx": table_snapshot["x"] - (link_counter * 26),
                                "my": table_snapshot["y"] + column_snapshot["y"],
                            }
                            column_snapshot["links"].append(link_snapshot)
                            link_counter += 1

                        table_snapshot["cols"].append(column_snapshot)
                        column_counter += 1

                    schema_snapshot["tables"].append(table_snapshot)

                snapshot.append(schema_snapshot)

            return snapshot

        determine_table_ordering()
        self.snapshot = create_snapshot()
        self.print_snapshot(how="raw")
        self.print_snapshot(how="pretty")
