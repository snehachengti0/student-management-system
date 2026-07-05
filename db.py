import mysql.connector
from mysql.connector import pooling
from config import Config

# Connection pool for efficient DB access
_pool = pooling.MySQLConnectionPool(
    pool_name="sms_pool",
    pool_size=5,
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
    autocommit=False,
)

def get_conn():
    return _pool.get_connection()

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """Helper that opens/closes a connection safely."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
        if commit:
            conn.commit()
            if cur.lastrowid:
                result = cur.lastrowid
        return result
    finally:
        cur.close()
        conn.close()
