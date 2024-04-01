from database import ConnectDB


def getschemafromdb(dbname):

    try:
        schema, _ = ConnectDB(
            dbname,
            """
            select name, sql from sqlite_master
            """,
        )
        tables_dict = {}
        for tables in schema:
            if tables[1] is not None:
                tables_dict[tables[0]] = tables[1]
        tables_dict["NA_tables"] = "NA"
        return tables_dict
    except Exception:
        print(Exception)
        print("something wrong getting schema")
