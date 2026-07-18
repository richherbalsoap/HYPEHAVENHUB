import os
import psycopg2

db_url = None
with open('.env.production', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.strip().split('=', 1)[1]
            # remove surrounding quotes if any
            if db_url.startswith('"') and db_url.endswith('"'):
                db_url = db_url[1:-1]
            break

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT order_id_id, status, description, created_at FROM store_ordertracking WHERE status = 'shiprocket_failed' ORDER BY created_at DESC LIMIT 5;")
for row in cur.fetchall():
    print(row)
conn.close()
