from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import redshift_connector
import json


# fernet = Fernet(Fernet.generate_key())
fernet = Fernet(b'Eur3dKoPu0q0L28peTM4hIqjjJYbEvyEb43L0etCeOs=')
redshift_connector.paramstyle = 'pyformat'

@dataclass
class DBInfo: host:str; port:int; name:str; user:str; pwd:str


def store_db_info(db:DBInfo, session):
    session['dbinfo'] = fernet.encrypt(json.dumps(asdict(db)).encode()).decode()

def load_db_info(session):
    if session['dbinfo']:
        return DBInfo(**json.loads(fernet.decrypt(session.get('dbinfo').encode()).decode()))
    else:
        return None 


def run_sql(query:str, db:DBInfo, args=None, fetch=True):
    try:
        with redshift_connector.connect(
            host=db.host, port=db.port, database=db.name, 
            user=db.user, password=db.pwd
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, args=args)

                if fetch:
                    results = cursor.fetchall()
                    return results
                else:
                    conn.commit()
                    return cursor.rowcount
        
    except Exception as e:
        print(f"Database error: {e}")

def test_conn(db:DBInfo):
    # test connection 
    return run_sql('SELECT 1', db, fetch=False)

def execute_query(query:str, session, args=None, fetch=True):
    try:
        db = load_db_info(session)
        return run_sql(query, db, args, fetch) if db else None
    except Exception as e:
        print(e)
        return None 