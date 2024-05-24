from database import ConnectDB


def test_ConnectDB():
    schema, _ = ConnectDB(
        "Samplefiles/FinancialSample.db",
        """
        select name, sql from sqlite_master
        """,
    )
    assert schema is not None
