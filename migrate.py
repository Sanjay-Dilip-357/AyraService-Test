import psycopg2
import sqlite3
import json
import datetime
import uuid
import time

PG_URL = "postgresql://00060db082:6c202e3fbe947ce0@proayra-instant.idb-node-01.symcloud.net:56578/proayra-instant?sslmode=require"
SQLITE_DB = "ayra_services.db"
CHUNK_SIZE = 20000

def get_pg_tables(pg_conn):
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        return [row[0] for row in cur.fetchall()]

def sanitize_value(val):
    """Converts complex types (JSON dicts, lists, datetimes, UUIDs) to SQLite-compatible values."""
    if val is None:
        return None
    # Convert JSON/Dicts and Lists to valid JSON strings
    if isinstance(val, (dict, list)):
        return json.dumps(val, default=str)
    # Convert Datetime/Date objects to ISO 8601 strings (fixes Python 3.12+ DeprecationWarning)
    if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
        return val.isoformat()
    # Convert UUIDs to strings
    if isinstance(val, uuid.UUID):
        return str(val)
    # Convert Booleans to 1 / 0 for SQLite
    if isinstance(val, bool):
        return 1 if val else 0
    return val

def migrate_table(pg_conn, sqlite_conn, table_name):
    print(f"\n[+] Migrating table: {table_name}...")
    start_time = time.time()
    
    # 1. Fetch column names & data types
    with pg_conn.cursor() as cur:
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cur.fetchall()

    if not columns:
        print(f"[-] Table {table_name} has no columns or doesn't exist.")
        return

    col_names = [col[0] for col in columns]
    
    # 2. Recreate Table in SQLite with appropriate types
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    
    sqlite_cols_def = []
    for name, dtype in columns:
        if dtype in ("integer", "smallint", "bigint", "serial", "bigserial", "boolean"):
            sqlite_type = "INTEGER"
        elif dtype in ("real", "double precision", "numeric", "decimal"):
            sqlite_type = "REAL"
        elif dtype in ("bytea",):
            sqlite_type = "BLOB"
        else: # text, varchar, char, json, jsonb, uuid, timestamp, date
            sqlite_type = "TEXT"
        sqlite_cols_def.append(f'"{name}" {sqlite_type}')
        
    create_sql = f'CREATE TABLE "{table_name}" ({", ".join(sqlite_cols_def)});'
    sqlite_cur.execute(create_sql)

    # 3. Stream data using a Server-Side Named Cursor
    cursor_name = f"stream_{table_name}"
    pg_named_cur = pg_conn.cursor(name=cursor_name)
    pg_named_cur.itersize = CHUNK_SIZE
    pg_named_cur.execute(f'SELECT * FROM "{table_name}"')

    # 4. Insert in Batches
    placeholders = ",".join(["?"] * len(col_names))
    insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'

    total_rows = 0
    while True:
        rows = pg_named_cur.fetchmany(CHUNK_SIZE)
        if not rows:
            break
        
        # Sanitize data (converting dicts -> JSON strings, dates -> strings, etc.)
        sanitized_rows = [
            tuple(sanitize_value(val) for val in row)
            for row in rows
        ]
        
        sqlite_cur.executemany(insert_sql, sanitized_rows)
        sqlite_conn.commit()
        total_rows += len(rows)
        print(f"  -> Transferred {total_rows:,} rows...", end="\r")

    pg_named_cur.close()
    elapsed = time.time() - start_time
    rate = int(total_rows / (elapsed or 1))
    print(f"\n[✔] Finished {table_name}: {total_rows:,} rows in {elapsed:.2f}s ({rate} rows/sec)")


def main():
    print("[*] Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(PG_URL)

    print(f"[*] Initializing SQLite Database: {SQLITE_DB}...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    
    # High performance settings for bulk writes
    sqlite_conn.execute("PRAGMA synchronous = OFF;")
    sqlite_conn.execute("PRAGMA journal_mode = MEMORY;")
    sqlite_conn.execute("PRAGMA cache_size = 1000000;")

    tables = get_pg_tables(pg_conn)
    print(f"[*] Found {len(tables)} tables to migrate: {', '.join(tables)}")

    for table in tables:
        migrate_table(pg_conn, sqlite_conn, table)

    sqlite_conn.execute("PRAGMA synchronous = NORMAL;")
    sqlite_conn.close()
    pg_conn.close()
    print("\n[🎉] All data successfully dumped into 'ayra_services.db'!")

if __name__ == "__main__":
    main()