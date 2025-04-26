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

# Define specific application tables to migrate
app_tables = [
    'users_customuser',
    'doctors_doctor',
    'appointments_appointment',
    'diet_exercise_dietplan',
    'diet_exercise_exerciseplan',
    'disease_prediction_prediction',
    'health_prediction_mentalhealthprediction',
    'health_prediction_pcosprediction',
    'health_prediction_obesityprediction',
    'subscriptions_subscription',
    'subscriptions_payment'
]

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

# For each specified table
for table_name in app_tables:
    print(f"Processing table: {table_name}")
    
    # First check if the table exists in SQLite
    sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    table_exists = sqlite_cursor.fetchone()
    
    if not table_exists:
        print(f"  - Table {table_name} does not exist in SQLite, skipping")
        continue
    
    # Get column names from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Get all data from the SQLite table
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        print(f"  - Found {len(rows)} rows to migrate")
        
        # Check if table exists in PostgreSQL
        try:
            pg_cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT 1;")
        except psycopg2.errors.UndefinedTable:
            print(f"  - Table {table_name} does not exist in PostgreSQL, skipping")
            pg_conn.rollback()
            continue
        
        # For each row, insert into PostgreSQL
        for row in rows:
            placeholders = ','.join(['%s'] * len(column_names))
            columns_str = ','.join([f'"{col}"' for col in column_names])
            
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