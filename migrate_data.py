import os
import django
import sqlite3
import psycopg2
from urllib.parse import urlparse
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicure.settings')
django.setup()

# Get the project base directory
BASE_DIR = Path(__file__).resolve().parent

# Parse the PostgreSQL connection URL
db_url = os.getenv('DATABASE_URL')
url = urlparse(db_url)
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

print(f"Connecting to PostgreSQL database: {dbname} on {host}")

# Connect to SQLite
sqlite_path = BASE_DIR / 'db.sqlite3'
print(f"Connecting to SQLite database at: {sqlite_path}")
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cursor = sqlite_conn.cursor()

# Get list of tables from SQLite (excluding Django system tables)
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'django_%' AND name NOT LIKE 'sqlite_%';")
tables = sqlite_cursor.fetchall()

print(f"Found {len(tables)} tables to migrate")

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
pg_cursor = pg_conn.cursor()

print("Starting data migration...")

# For each table
for table in tables:
    table_name = table[0]
    print(f"Processing table: {table_name}")
    
    # Get column names from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Get all data from the SQLite table
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        print(f"  - Found {len(rows)} rows to migrate")
        
        # For each row, insert into PostgreSQL
        for row in rows:
            placeholders = ','.join(['%s'] * len(column_names))
            columns_str = ','.join([f'"{col}"' for col in column_names])  # Quote column names
            
            try:
                pg_cursor.execute(
                    f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})', 
                    row
                )
            except Exception as e:
                print(f"  - Error inserting into {table_name}: {e}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"  - Migration completed for table {table_name}")
    else:
        print(f"  - No data found in table {table_name}")

print("Data migration completed!")

# Close connections
sqlite_cursor.close()
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()