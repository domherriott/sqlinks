from sqlinks.app.helpers import deconstruct_sid, clean_sid


class Object:
    object_counter = 1

    def __init__(self, sid):
        # String ID
        self.sid = sid
        # Numerical ID
        self.nid = Object.object_counter
        Object.object_counter += 1


class Table(Object):
    def __init__(self, sid: str):
        Object.__init__(self, sid)

        schema_sid, table_sid = deconstruct_sid(sid, how="table")

        self.sid = table_sid
        self.schema_sid = schema_sid
        self.name = table_sid.split(".")[1]


class Link(Object):
    def __init__(self, source_table_sid: str, target_table_sid: str):
        Object.__init__(self, sid=None)
        self.source_table_sid = source_table_sid
        self.target_table_sid = target_table_sid


class Collection:
    def __init__(self):
        self.tables = {}
        self.links = []

    def add_table(self, sid: str):
        sid = clean_sid(sid)

        if sid in self.tables:
            return
        self.tables[sid] = Table(sid=sid)

    def add_link(self, source_table_sid: int, target_table_sid: int):
        source_table_sid = clean_sid(source_table_sid)
        target_table_sid = clean_sid(target_table_sid)

        self.links.append(
            Link(source_table_sid=source_table_sid, target_table_sid=target_table_sid)
        )
