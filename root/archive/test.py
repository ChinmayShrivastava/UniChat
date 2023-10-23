import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['SQL_URL']
# connect to postgres
conn = psycopg2.connect(DATABASE_URL)
# create a cursor
cur = conn.cursor()

# cur.execute("ALTER TABLE urls ADD COLUMN embedded BOOLEAN DEFAULT FALSE")
# conn.commit()

# get all table names
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cur.fetchall()

# loop through tables and print schema and initial entries
for table in tables:
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table[0]}'")
    schema = cur.fetchall()
    print(f"Schema for {table[0]}:")
    for column in schema:
        print(f"{column[0]}: {column[1]}")
    cur.execute(f"SELECT * FROM {table[0]} LIMIT 5")
    entries = cur.fetchall()
    print(f"Initial entries for {table[0]}:")
    for entry in entries:
        print(entry)

# close cursor and connection
cur.close()
conn.close()