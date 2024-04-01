import sqlite3


def ConnectDB(dbname, query):
    try:
        with sqlite3.connect(dbname) as con:
            cursor = con.cursor()
            data = cursor.execute(query)
            # Fetch all the results
            results = cursor.fetchall()

            cursor.close()

            return results, data.description
    except sqlite3.Error as e:
        print("ConnectDB failed:")
        print(e)  # prints the error message


def CreateDBformSQL(sqlfile):
    # Open the SQL file
    with open(sqlfile + ".sql", "r") as f:
        # Create a connection to the database
        conn = sqlite3.connect(f"{sqlfile}.db")
        # Create a cursor object
        cur = conn.cursor()
        # Execute the SQL commands in the file
        cur.executescript(f.read())
        # Commit the changes
        conn.commit()
        # Close the connection
        conn.close()


def Pandasdb(filename, df):
    try:
        with sqlite3.connect("tempfiles/" + filename + ".db") as conn:
            # Create a cursor object
            cur = conn.cursor()

            # Write the data to a sqlite db table
            df.to_sql(filename, conn, if_exists="replace", index=False)

            # Close connection to SQLite database
            cur.close()
    except sqlite3.Error as e:
        print("Pandasdb failed:")
        print(e)  # prints the error message
