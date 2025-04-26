import os
import psycopg2
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')

# Parse the URL properly
result = urllib.parse.urlparse(database_url)
username = result.username
password = result.password
database = result.path[1:]  # Remove leading slash
hostname = result.hostname
port = result.port

# Connect to the database
conn = psycopg2.connect(
    dbname=database,
    user=username,
    password=password,
    host=hostname,
    port=port
)

cursor = conn.cursor()

# Check users table
try:
    cursor.execute("SELECT COUNT(*) FROM users_customuser;")
    user_count = cursor.fetchone()[0]
    print(f"Number of users in database: {user_count}")

    # List some users if they exist
    if user_count > 0:
        cursor.execute("SELECT id, email, is_active FROM users_customuser LIMIT 5;")
        users = cursor.fetchall()
        print("Sample users:")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
except Exception as e:
    print(f"Error querying database: {e}")

# Close the connection
cursor.close()
conn.close()