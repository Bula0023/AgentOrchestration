import sqlite3
from .schemas import DatabaseQueryInput, DatabaseQueryOutput

def query_database(args: DatabaseQueryInput) -> DatabaseQueryOutput:
    query = args.query.strip().lower()
    if not query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for safety reasons.")
    
    # connect to the database
    connection = sqlite3.connect('app.db')
    #Make each row like a dictionary
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()
        cursor.execute(args.query)
        rows = cursor.fetchall()
        results = [
            dict(row)
            for row in rows
        ]
        return DatabaseQueryOutput(rows=results)
    finally:
        connection.close()

