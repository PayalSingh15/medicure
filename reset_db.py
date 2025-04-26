import os
import django
import psycopg2
from urllib.parse import urlparse

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicure.settings')
django.setup()

# Parse the PostgreSQL connection URL
db_url = os.getenv('DATABASE_URL')
url = urlparse(db_url)
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

print(f"Connecting to PostgreSQL database: {dbname} on {host}")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Tables to truncate in reverse order of their dependencies
tables = [
    'subscriptions_payment',
    'subscriptions_subscription',
    'health_prediction_obesityprediction',
    'health_prediction_pcosprediction',
    'health_prediction_mentalhealthprediction',
    'disease_prediction_prediction',
    'diet_exercise_exerciseplan',
    'diet_exercise_dietplan',
    'appointments_appointment',
    'doctors_doctor',
    'users_customuser'
]

print("Clearing tables...")

for table in tables:
    try:
        print(f"Truncating {table}...")
        cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
        print(f"  - Table {table} truncated successfully")
    except Exception as e:
        print(f"  - Error truncating {table}: {e}")

print("Database reset completed!")

cursor.close()
conn.close()